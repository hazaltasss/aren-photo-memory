# Aren Photo Memory 📸

Aren'in tüm anlarını yapay zeka ile kaydet, analiz et ve anlamsal (semantic) olarak sorgula. 2 yaşındaki Aren için özel olarak tasarlanmış, fotoğraf analiz ve arama sistemi.

## 🚀 Özellikler

- **AI Fotoğraf Analizi:** Google Gemini Vision (2.5 Flash) ile fotoğraflardaki duygu, aktivite, mekan ve nesnelerin otomatik tespiti.
- **Anlamsal Arama:** "Aren'in çimenlerde güldüğü anlar" gibi doğal dilde sorgularla fotoğraf bulma.
- **Türkçe Dil Desteği:** Tüm analizler ve açıklamalar otomatik olarak Türkçe üretilir.
- **Akıllı Filtreleme:** Benzerlik eşiği (threshold) sayesinde sadece gerçekten alakalı sonuçları görme.
- **Modern Arayüz:** React, Tailwind CSS ve glassmorphism detaylarıyla şık ve hızlı bir kullanıcı deneyimi.
- **Detaylı Görünüm:** Fotoğraflara tıklayarak AI tarafından üretilen tüm detaylı analizleri ve tam metin açıklamaları görebilme.

## 🛠 Teknoloji Yığını

- **Backend:** FastAPI (Python 3.12)
- **Frontend:** React (Vite, TypeScript, Tailwind CSS)
- **Yapay Zeka:** Google Gemini 2.5 Flash (Vision) & Gemini Embedding 2
- **Veritabanı:** SQLite + `sqlite-vec` (Vektör arama desteği)
- **State Yönetimi:** Redux Toolkit & RTK Query

## 📦 Kurulum ve Çalıştırma

Proje yönetimini kolaylaştırmak için `Makefile` kullanıyoruz.

### 1. Hazırlık
- `backend/.env` dosyasını oluşturun ve `GEMINI_API_KEY` değerinizi ekleyin.
```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=gemini-embedding-2
DATABASE_URL=sqlite:///./aren.db
UPLOAD_DIR=./uploads
SEARCH_THRESHOLD=0.5
```

### 2. Kurulum
Tüm bağımlılıkları yüklemek için:
```bash
make install
```

### 3. Çalıştırma
Frontend ve Backend'i aynı anda başlatmak için:
```bash
make dev
```

### Diğer Komutlar
- `make run-backend`: Sadece backend'i başlatır.
- `make run-frontend`: Sadece frontend'ı başlatır.
- `make stop`: Çalışan tüm servisleri durdurur.
- `make clean`: Geçici dosyaları ve veritabanını temizler.

## 📄 Dokümantasyon

Daha detaylı teknik bilgi için `docs/` klasörüne göz atabilirsiniz:
- [Mimari Detayları](docs/architecture.md)

## 🛡️ Lisans
Bu proje kişisel kullanım için geliştirilmiştir.
