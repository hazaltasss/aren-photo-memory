# WhatsApp Bot Entegrasyonu Tasarımı (Twilio)

## Hedef
Kullanıcıların WhatsApp üzerinden doğal dilde anı sormasını ve sistemin en alakalı fotoğrafı otomatik olarak geri göndermesini sağlamak.

## Teknik Mimari

### 1. Webhook Akışı
- **Twilio Sandbox:** Kullanıcıdan gelen mesajı alır ve bizim `/api/whatsapp/webhook` adresimize bir POST isteği (form-data) atar.
- **Backend:**
    - Gelen `Body` içeriğini alır.
    - `search_photos` fonksiyonunu kullanarak AI araması yapar.
    - Bulunan ilk fotoğrafın tam URL'ini oluşturur.
    - Twilio'ya **TwiML (XML)** formatında yanıt döner.

### 2. Gereksinimler
- **Kütüphane:** `twilio` (Python)
- **Ortam Değişkenleri:**
    - `TWILIO_ACCOUNT_SID`
    - `TWILIO_AUTH_TOKEN`
    - `TWILIO_PHONE_NUMBER` (Sandbox numarası)
    - `BASE_PUBLIC_URL` (Ngrok URL'i)

## Uygulama Adımları

### 1. Backend Router (`whatsapp.py`)
- `Body` parametresini oku.
- Semantic search'ü tetikle.
- `MessagingResponse` kullanarak fotoğrafı gönder.

### 2. Statik Dosya Erişimi
- `/uploads` klasörünün dışarıdan (Public URL) erişilebilir olduğundan emin ol (Uvicorn static files).

### 3. Ngrok Yapılandırması
- `ngrok http 8000` komutu ile yerel portu internete aç.
- Twilio Console'da Webhook URL'ini güncelle.
