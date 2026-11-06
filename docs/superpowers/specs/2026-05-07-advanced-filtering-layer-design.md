# Gelişmiş Filtreleme Katmanı Tasarımı (Advanced Filtering Layer)

## Hedef
Aren Photo Memory sistemine, mevcut anlamsal (semantic) arama ile entegre çalışan, yapılandırılmış metadata tabanlı bir filtreleme sistemi eklemek.

## Teknik Mimari

### 1. Hibrit Sorgu Mantığı (Backend)
- **Endpoint:** `/api/search` (POST)
- **Yeni İstek Şeması:**
  ```json
  {
    "query": "opsiyonel metin",
    "filters": {
      "emotions": ["mutlu", "meraklı"],
      "location_types": ["dış mekan"],
      "objects": ["top", "oyuncak"],
      "date_range": {"start": "ISO-DATE", "end": "ISO-DATE"},
      "hair_length": "kısa"
    },
    "limit": 20
  }
  ```
- **Sorgu Akışı:**
  1. Eğer `query` varsa -> Vector search ile benzerlik skorlarını al.
  2. SQL sorgusuna `filters` içindeki her alan için `AND` koşulları ekle.
  3. Hem anlamsal hem yapısal filtrelerden geçen sonuçları dön.

### 2. Dinamik Filtre Seçenekleri
- **Endpoint:** `/api/filters/options` (GET)
- **Görevi:** Veritabanını tarayarak mevcut tüm duyguları, mekanları ve en popüler (top 5-10) nesneleri listeler. Bu sayede filtre barı her zaman güncel kalır.

## Arayüz Tasarımı (Frontend)

### 1. Yatay Filtre Barı (Horizontal Filter Bar)
- **Konum:** Arama çubuğunun hemen altı.
- **Stil:** Glassmorphism (beyaz şeffaf, backdrop-blur).
- **Bileşenler:**
  - **Duygu Filtresi:** Çoklu seçim yapılabilen popover.
  - **Mekan Filtresi:** Hızlı seçim butonları.
  - **Nesne Filtresi:** En popüler 5 nesne çipi + "Farklı ara..." input alanı.
  - **Zaman Filtresi:** Hızlı aralıklar (Son 1 ay, Geçen Yaz) + Takvim ikonu.

### 2. Filtre Durum Yönetimi (State Management)
- Tüm filtreler `activeFilters` adında bir merkezi state'te tutulur.
- Herhangi bir filtre değiştiğinde arama otomatik olarak tetiklenir (veya "Uygula" butonu eklenir).

## Verifikasyon Planı
- "Parkta oyun" araması yapılıp üzerine "Mutlu" filtresi eklendiğinde sadece ilgili fotoğrafların geldiği doğrulanacak.
- Hiçbir filtre seçili değilken genel galeri görünümü bozulmamalı.
- Manuel nesne araması (input) hem chiplerle hem de anlamsal aramayla uyumlu çalışmalı.
