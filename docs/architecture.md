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
│                 │         │  │ Vision   │  │  + Vec    │ │
│                 │         │  └──────────┘  └───────────┘ │
│                 │         │  ┌──────────────────────────┐ │
│                 │         │  │  /uploads (foto storage) │ │
│                 │         └──┴──────────────────────────┴─┘
└─────────────────┘
```

**Monorepo yapısı:**
- `aren/backend/` — FastAPI, Python
- `aren/frontend/` — React + Vite, TypeScript

**Temel Akış:**
1. Kullanıcı frontend'den fotoğraf yükler.
2. Backend fotoğrafı kaydeder, Gemini Vision API'ye gönderir.
3. Gemini'den dönen analiz (Türkçe yapısal alanlar + açıklama + embedding) SQLite'a yazılır.
4. Kullanıcı doğal dil sorgusu yapar.
5. Backend sorguyu embedding'e çevirir, `sqlite-vec` ile benzerlik araması + threshold filtrelemesi ile sonuç döner.

---

## Veri Modeli

### Yaklaşım: Hibrit (Structured + Free-form)

Her fotoğraf için hem sabit yapısal alanlar çıkarılır (filtreleme için) hem de serbest bir doğal dil açıklaması alınır (semantic search için). Tüm metinler **Türkçe** olarak üretilir.

### Yapısal Alanlar (filtrelenebilir)

| Alan | Tip | Örnek | Açıklama |
|------|-----|-------|----------|
| `emotion` | enum | `mutlu`, `üzgün`, `şaşkın`, `nötr`, `kızgın`, `heyecanlı`, `uykulu` | Aren'in baskın duygusu |
| `is_smiling` | bool | `true` | Gülümsüyor mu? |
| `is_crying` | bool | `false` | Ağlıyor mu? |
| `activity` | string | `çimenlerde oynuyor`, `yemek yiyor` | Ne yapıyor? |
| `location_type` | enum | `iç mekan`, `dış mekan` | Mekan tipi |
| `location_detail` | string | `park`, `ev`, `plaj` | Mekan detayı |
| `people_count` | int | `3` | Fotoğraftaki kişi sayısı |
| `has_other_people` | bool | `true` | Aren dışında biri var mı? |
| `clothing_description` | string | `mavi tişört, beyaz şort` | Kıyafet açıklaması |
| `hair_length` | enum | `kısa`, `orta`, `uzun` | Saç uzunluğu |
| `is_funny` | bool | `true` | Komik/eğlenceli bir an mı? |
| `funniness_score` | int (1-10) | `8` | Ne kadar komik |
| `cuteness_score` | int (1-10) | `9` | Tatlılık skoru |
| `objects` | list[string] | `["oyuncak", "top", "bisiklet"]` | Nesneler |
| `season_guess` | enum | `ilkbahar`, `yaz`, `sonbahar`, `kış` | Tahmini mevsim |

### Serbest Alanlar (semantic search için)

| Alan | Tip | Açıklama |
|------|-----|----------|
| `description` | text | Fotoğrafın detaylı Türkçe açıklaması (Gemini'den) |
| `description_embedding` | vector (3072) | Açıklamanın `gemini-embedding-2` vektörü |

---

## API Tasarımı

### Endpoints

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `POST` | `/api/photos` | Fotoğraf yükle → Gemini analiz (Türkçe) → DB'ye kaydet |
| `GET` | `/api/photos` | Tüm fotoğrafları listele |
| `GET` | `/api/photos/image/{filename}` | Fotoğraf dosyasını getir |
| `POST` | `/api/search` | Anlamsal arama (Threshold destekli) |

---

## Teknoloji Stack

| Katman | Teknoloji | Neden |
|--------|-----------|-------|
| Backend | Python 3.12 + FastAPI | AI ekosistemi, performans |
| Vision | Google Gemini (`gemini-2.5-flash`) | Çok modlu analiz |
| Embedding | `gemini-embedding-2` | 3072 boyutlu anlamsal vektörler |
| Database | SQLite + `sqlite-vec` | Vektör aramalı lokal DB |
| Frontend | React + Vite + TypeScript | Modern UI/UX |

---

## Versiyon Geçmişi

| Tarih | Değişiklik |
|-------|------------|
| 2026-05-06 | İlk mimari tasarım (MVP) |
| 2026-05-06 | Türkçe dil desteği, 3072 boyutlu embedding ve Search Threshold eklendi |
