from fastapi import APIRouter, Request, Response, Form
from fastapi.concurrency import run_in_threadpool
from twilio.twiml.messaging_response import MessagingResponse
from app.services.search_service import perform_search
from app.services.gemini import get_gemini_model 
from app.config import settings
from app.services.photo_service import process_and_save_photo
import os
import json
import requests
import uuid

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])

async def parse_query_with_ai(user_msg: str):
    """
    Kullanıcının doğal dil mesajını yapılandırılmış filtreye dönüştürür.
    """
    models = get_gemini_model()
    prompt = f"""
    Kullanıcı bir fotoğraf arşivi için şu mesajı gönderdi: "{user_msg}"
    
    Bu mesajı aşağıdaki JSON formatına dönüştür. Sadece JSON dön.
    {{
        "query": "kalan arama metni",
        "filters": {{
            "emotions": ["mutlu", "üzgün", "şaşkın", "nötr", "kızgın", "heyecanlı", "uykulu"],
            "location_types": ["iç mekan", "dış mekan"],
            "objects": ["top", "oyuncak", "kitap"]
        }}
    }}
    
    KRİTİK KURALLAR:
    1. Kullanıcı "güldüğü", "mutlu olduğu" gibi ifadeler kullandığında BUNU KESİNLİKLE "emotions": ["mutlu"] filtresine çevir.
    2. Eğer bir filtre (örneğin duygu) yakaladıysan, o kelimeyi "query" alanından ÇIKAR! Örneğin "Aren'in güldüğü park fotoğrafı" mesajı için query sadece "Aren park" olmalıdır. "Gülmek" kelimesi query'de KALMAMALIDIR.
    3. Bu sayede vektörel arama motoru, arkada gülen başka insanları yanlışlıkla Aren sanıp getirmeyecek.
    """
    try:
        # Model ismini settings'den alıyoruz
        response = models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt
        )
        json_str = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(json_str)
    except Exception as e:
        print(f"AI Parse Hatası: {e}")
        return {"query": user_msg, "filters": {}}

@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()
    body = form_data.get("Body", "")
    from_number = form_data.get("From", "")
    num_media = int(form_data.get("NumMedia", 0))
    
    print(f"📥 WhatsApp'tan Mesaj Geldi: '{body}' (Media: {num_media})")
    
    response = MessagingResponse()
    msg = response.message()
    
    try:
        # Eğer medyalı bir mesajsa -> Yükleme (Upload) İşlemi
        if num_media > 0:
            media_url = form_data.get("MediaUrl0")
            content_type = form_data.get("MediaContentType0", "")
            
            print(f"📸 Fotoğraf indiriliyor: {media_url}")
            
            # Twilio'dan fotoğrafı indir
            auth = None
            if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
                auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            else:
                print("⚠️ UYARI: Twilio SID veya Auth Token ayarlanmamış! WhatsApp medya indirme işlemi muhtemelen 401 Unauthorized hatası verecek.")
            
            try:
                img_resp = requests.get(media_url, auth=auth, allow_redirects=True)
                if img_resp.status_code == 200:
                    photo_id = str(uuid.uuid4())
                    ext = ".jpg"
                    if "png" in content_type: ext = ".png"
                    elif "mp4" in content_type: ext = ".mp4"
                    
                    filename = f"{photo_id}{ext}"
                    file_path = os.path.join(settings.UPLOAD_DIR, filename)
                    
                    with open(file_path, "wb") as f:
                        f.write(img_resp.content)
                    
                    print("🧠 Yapay Zeka analiz ediyor ve kaydediliyor...")
                    photo_response = await run_in_threadpool(process_and_save_photo, file_path, filename)
                    
                    msg.body(f"Harika bir anı! 🛡️✨\n\nAren'in bu anısını güvenle arşive ekledim.\n😊 Duygu: {photo_response.emotion}\n📝 Özet: {photo_response.description}")
                else:
                    error_msg = f"HTTP {img_resp.status_code}: {img_resp.text[:100]}"
                    print(f"❌ Medya indirme hatası: {error_msg}")
                    msg.body(f"Fotoğrafı indirirken bir sorun oluştu.\nHata Detayı: {error_msg}")
            except Exception as e:
                print(f"❌ İstek hatası: {str(e)}")
                if 'file_path' in locals() and os.path.exists(file_path):
                    os.remove(file_path)
                msg.body(f"Fotoğraf indirilirken sunucu hatası oluştu: {str(e)}")
                
            return Response(content=str(response), media_type="application/xml")

        # Eğer medyası yoksa -> Arama (Search) İşlemi
        print("🧠 Kullanıcı niyeti analiz ediliyor...")
        ai_request = await parse_query_with_ai(body)
        print(f"🎯 AI Niyeti: {ai_request}")

        # 2. Hibrit Arama Yap (Artık filtrelerle birlikte!)
        results = perform_search(
            query=ai_request.get("query"), 
            filters=ai_request.get("filters"), 
            limit=1
        )
        
        
        if results:
            photo = results[0]
            base_url = settings.BASE_PUBLIC_URL or "http://localhost:8000"
            photo_url = f"{base_url}{photo['file_url']}"
            print(f"✅ Sonuç Bulundu: {photo_url}")
            
            msg.body(f"Aren'ın en alakalı anısını buldum! 🛡️✨\n\n📍 {photo['location_detail']} \n😊 Duygu: {photo['emotion']} \n📝 AI Özeti: {photo['description']}")
            msg.media(photo_url)
        else:
            print("❌ Sonuç bulunamadı.")
            msg.body("Maalesef istediğin kriterlere uygun bir anı bulamadım. 😔")
            
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        print(f"🚨 HATA: {str(e)}")
        return Response(content="Error", status_code=500)
