# Aren — Photo Memory System Architecture

> Aren'in tüm anlarını AI ile kaydet, analiz et ve sorgula.

## Genel Bakış

Aren, 2 yaşındaki bir çocuğun fotoğraflarını yükleyerek AI (Google Gemini) ile analiz eden, yapısal veriler çıkaran ve bu veriler üzerinde doğal dil sorgusu yapılmasını sağlayan bir web uygulamasıdır.

**Örnek sorgular:**
- "Aren'in güldüğü fotoğraflar"
- "Saçının kısa olduğu zamanlar"
- "Aren'in komik göründüğü top 5 an"

---

## Sistem Mimarisi

```
┌─────────────────┐         ┌─────────────────────────────┐
│                 │         │         FastAPI Backend       │
│   React (Vite)  │◄──API──►│                              │
│   Frontend      │         │  ┌──────────┐  ┌───────────┐ │
│                 │         │  │ Gemini   │  │  SQLite   │ │
└─────────────────┘         │  │ Vision   │  │  + Vec    │ │
                            │  └──────────┘  └───────────┘ │
                            │  ┌──────────────────────────┐ │
                            │  │  /uploads (foto storage) │ │
                            └──┴──────────────────────────┴─┘
```

**Monorepo yapısı:**
- `aren/backend/` — FastAPI, Python
- `aren/frontend/` — React + Vite, TypeScript

**Temel Akış:**
1. Kullanıcı frontend'den fotoğraf yükler
2. Backend fotoğrafı kaydeder, Gemini Vision API'ye gönderir
3. Gemini'den dönen analiz (yapısal alanlar + serbest açıklama + embedding) SQLite'a yazılır
4. Kullanıcı doğal dil sorgusu yapar
5. Backend sorguyu embedding'e çevirir, semantic search + yapısal filtreleme ile sonuç döner

---

## Veri Modeli

### Yaklaşım: Hibrit (Structured + Free-form)

Her fotoğraf için hem sabit yapısal alanlar çıkarılır (filtreleme için) hem de serbest bir doğal dil açıklaması alınır (semantic search için).

### Yapısal Alanlar (filtrelenebilir)

| Alan | Tip | Örnek | Açıklama |
|------|-----|-------|----------|
| `emotion` | enum | `happy`, `sad`, `surprised`, `neutral`, `angry`, `excited`, `sleepy` | Aren'in baskın duygusu |
| `is_smiling` | bool | `true` | Gülümsüyor mu? |
| `is_crying` | bool | `false` | Ağlıyor mu? |
| `activity` | string | `playing`, `eating`, `sleeping`, `bathing`, `reading` | Ne yapıyor? |
| `location_type` | enum | `indoor`, `outdoor` | İç mekan / dış mekan |
| `location_detail` | string | `park`, `ev`, `restoran`, `bahçe` | Mekan detayı |
| `people_count` | int | `3` | Fotoğraftaki kişi sayısı |
| `has_other_people` | bool | `true` | Aren dışında biri var mı? |
| `clothing_description` | string | `kırmızı tişört, kot şort` | Kıyafet açıklaması |
| `hair_length` | enum | `short`, `medium`, `long` | Saç uzunluğu |
| `is_funny` | bool | `true` | Komik/eğlenceli bir an mı? |
| `funniness_score` | int (1-10) | `8` | Ne kadar komik (top N sorguları için) |
| `cuteness_score` | int (1-10) | `9` | Tatlılık skoru |
| `objects` | list[string] | `["oyuncak", "top", "bisiklet"]` | Fotoğraftaki önemli nesneler |
| `season_guess` | enum | `spring`, `summer`, `fall`, `winter` | Tahmini mevsim |

### Serbest Alanlar (semantic search için)

| Alan | Tip | Açıklama |
|------|-----|----------|
| `description` | text | Fotoğrafın detaylı doğal dil açıklaması (Gemini'den) |
| `description_embedding` | vector | Açıklamanın embedding vektörü (semantic search için) |

### Meta Veriler

| Alan | Tip | Açıklama |
|------|-----|----------|
| `id` | UUID | Kayıt ID |
| `file_path` | string | Fotoğraf dosya yolu |
| `uploaded_at` | datetime | Yükleme zamanı |
| `photo_date` | date (nullable) | Fotoğrafın çekildiği tarih (EXIF veya kullanıcı girişi) |
| `notes` | text (nullable) | Kullanıcının eklediği not |

---

## API Tasarımı

### Endpoints

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `POST` | `/api/photos` | Fotoğraf yükle → Gemini analiz → DB'ye kaydet |
| `GET` | `/api/photos` | Tüm fotoğrafları listele (pagination) |
| `GET` | `/api/photos/{id}` | Tek fotoğraf detayı |
| `DELETE` | `/api/photos/{id}` | Fotoğraf sil |
| `POST` | `/api/photos/search` | Doğal dil sorgusu (semantic search) |
| `PATCH` | `/api/photos/{id}` | Not ekle/güncelle, tarih düzelt |

### Fotoğraf Yükleme Akışı

```
Client                    Backend                   Gemini
  │                          │                         │
  │── POST /api/photos ─────►│                         │
  │   (multipart: image)     │── analyze(image) ──────►│
  │                          │◄── structured JSON ─────│
  │                          │── generate embedding ──►│
  │                          │◄── vector ──────────────│
  │                          │── save to SQLite        │
  │◄── 201 + photo data ────│                         │
```

### Arama Akışı

```
Client                    Backend                   Gemini
  │                          │                         │
  │── POST /api/search ─────►│                         │
  │   {"query": "Aren'in     │── embed(query) ────────►│
  │    güldüğü anlar"}       │◄── query vector ────────│
  │                          │── SQLite: cosine        │
  │                          │   similarity search     │
  │◄── [photo results] ─────│                         │
```

### Yanıt Formatı (Örnek)

```json
{
  "id": "uuid-123",
  "file_url": "/uploads/photo_001.jpg",
  "photo_date": "2026-05-01",
  "emotion": "happy",
  "is_smiling": true,
  "activity": "playing",
  "location_type": "outdoor",
  "description": "Aren parkta yeşil bir topla oynuyor, gülümsüyor...",
  "funniness_score": 7,
  "cuteness_score": 9,
  "uploaded_at": "2026-05-06T12:00:00Z"
}
```

---

## Frontend Sayfaları (MVP)

### 1. Ana Sayfa / Galeri
- Fotoğrafların grid görünümü
- Üstte arama çubuğu — doğal dil sorgusu
- Her fotoğraf kartında: küçük resim, tarih, duygu ikonu, kısa açıklama

### 2. Fotoğraf Yükleme
- Drag & drop veya dosya seçici (çoklu yükleme destekli)
- Gemini analizi sırasında loading durumu
- Analiz sonucu önizlemesi
- Opsiyonel: tarih ve not ekleme

### 3. Fotoğraf Detay
- Büyük fotoğraf görünümü
- Tüm analiz alanları
- Serbest açıklama metni
- Not ekleme/düzenleme
- Silme butonu

### Sonraki İterasyonlar
- Filtre paneli (dropdown ile duygu, mekan, aktivite filtreleme)
- Zaman çizelgesi görünümü
- İstatistik dashboard (en çok gülümsediği ay, en sık aktiviteler)
- Toplu yükleme ilerleme çubuğu
- Daha gelişmiş UI/UX tasarımı

---

## Teknoloji Stack

| Katman | Teknoloji | Neden |
|--------|-----------|-------|
| Backend | Python 3.12 + FastAPI | AI ekosistemi, hızlı API geliştirme |
| Vision | Google Gemini API (`gemini-2.0-flash`) | Fiyat/performans, vision + embedding tek API |
| Embedding | Gemini `text-embedding-004` | Semantic search, aynı ekosistem |
| Database | SQLite + `sqlite-vec` | MVP için sıfır kurulum, vektör arama desteği |
| Frontend | React + Vite + TypeScript | Modern, hızlı, geniş ekosistem |
| Dosya Storage | Lokal dosya sistemi (`/uploads`) | MVP için yeterli |

---

## Proje Yapısı

```
aren/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS config
│   │   ├── config.py            # Ayarlar, env variables
│   │   ├── models.py            # SQLite tablo tanımları
│   │   ├── database.py          # DB bağlantısı, migration
│   │   ├── routers/
│   │   │   ├── photos.py        # Upload, list, delete endpoints
│   │   │   └── search.py        # Arama endpoint'leri
│   │   ├── services/
│   │   │   ├── gemini.py        # Gemini Vision + Embedding çağrıları
│   │   │   ├── analyzer.py      # Fotoğraf analiz orchestration
│   │   │   └── search.py        # Semantic + structured search logic
│   │   └── schemas.py           # Pydantic request/response models
│   ├── uploads/                 # Yüklenen fotoğraflar
│   ├── aren.db                  # SQLite veritabanı
│   ├── requirements.txt
│   └── .env                     # GEMINI_API_KEY
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── pages/
│   │   │   ├── Gallery.tsx      # Ana galeri + arama
│   │   │   ├── Upload.tsx       # Fotoğraf yükleme
│   │   │   └── PhotoDetail.tsx  # Fotoğraf detay
│   │   ├── components/
│   │   │   ├── PhotoCard.tsx    # Galeri kartı
│   │   │   ├── SearchBar.tsx    # Arama çubuğu
│   │   │   └── UploadZone.tsx   # Drag & drop alan
│   │   └── api/
│   │       └── client.ts        # Backend API çağrıları
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   └── architecture.md          # Bu doküman
└── README.md
```

---

## Gemini API Key Kurulumu

1. [Google AI Studio](https://aistudio.google.com/apikey) adresine git
2. "Create API Key" tıkla
3. Key'i kopyala
4. `backend/.env` dosyasına ekle: `GEMINI_API_KEY=your_key_here`

---

## Versiyon Geçmişi

| Tarih | Değişiklik |
|-------|------------|
| 2026-05-06 | İlk mimari tasarım (MVP) |
