# 🌿 AgenticSQL

AgenticSQL, doğal dil sorguları ile SQL veritabanlarını yönetmenizi sağlayan yapay zeka destekli bir veri arayüzüdür. SQLite ve Oracle veritabanlarına bağlanarak karmaşık sorguları otomatik olarak oluşturur, çalıştırır ve sonuçları Türkçe açıklamalarla sunar.

---

## ✨ Özellikler

- **Doğal Dil ile Sorgulama** — SQL bilgisi gerektirmeden veritabanınıza Türkçe soru sorun
- **Çoklu Veritabanı Desteği** — SQLite dosyaları ve Oracle bağlantıları aynı arayüzden yönetilir
- **Birden Fazla Oracle Bağlantısı** — Kayıtlı Oracle bağlantılarını ekleyin, seçin ve silin
- **Claude Model Seçimi** — Sonnet, Opus ve Haiku arasında anlık geçiş yapın
- **Güvenlik Kısıtlamaları** — DROP, DELETE ve ALTER komutları engellenir
- **Konuşma Geçmişi** — Önceki mesajları hatırlayarak bağlamsal sorgulama yapar
- **Login Ekranı** — Kullanıcı adı ve şifre ile koruma
- **Modern Arayüz** — Yeşil temalı, temiz ve sade Streamlit UI

---

## 🛠️ Teknoloji Yığını

| Katman | Teknoloji |
|---|---|
| Dil | Python 3.13+ |
| UI | Streamlit |
| LLM | Claude (Anthropic) — Sonnet / Opus / Haiku |
| Agent Framework | LangGraph `create_react_agent` |
| DB Araçları | LangChain Community SQL Toolkit |
| ORM | SQLAlchemy |
| SQLite Sürücü | Python built-in `sqlite3` |
| Oracle Sürücü | `python-oracledb` (Thin Mode) |
| İzleme | LangSmith |
| Test | Pytest |

---

## 📁 Proje Yapısı

```
AgenticSQL/
├── agenticsql.py              # Ana uygulama giriş noktası
├── managers/
│   ├── agent_manager.py       # LLM ve agent kurulumu
│   ├── database_manager.py    # SQLite / Oracle bağlantı yönetimi
│   ├── login_manager.py       # Kimlik doğrulama
│   ├── session_manager.py     # Oturum ve sohbet geçmişi
│   └── ui_manager.py          # Streamlit UI bileşenleri
├── Database/
│   ├── *.sqlite               # SQLite veritabanı dosyaları
│   └── oracle_connections.json # Kayıtlı Oracle bağlantıları
├── tests/                     # Pytest test dosyaları
├── .env                       # Ortam değişkenleri
└── requirements.txt
```

---

## ⚙️ Kurulum

### 1. Repoyu klonlayın

```bash
git clone https://github.com/mehmetalikoker/AgenticSQL.git
cd AgenticSQL
```

### 2. Sanal ortam oluşturun

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS / Linux
```

### 3. Bağımlılıkları yükleyin

```bash
pip install -r requirements.txt
```

### 4. `.env` dosyasını yapılandırın

Proje kökünde `.env` dosyası oluşturun:

```env
# Uygulama girişi
APP_USERNAME=admin
APP_PASSWORD=admin123

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# LangSmith izleme (opsiyonel)
LANGCHAIN_API_KEY=lsv2_...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=AgenticSQL

# Oracle bağlantısı (opsiyonel — UI'dan da eklenebilir)
ORACLE_HOST=
ORACLE_PORT=1521
ORACLE_SERVICE=
ORACLE_USER=
ORACLE_PASSWORD=
```

### 5. SQLite veritabanı ekleyin

`Database/` klasörüne `.sqlite` veya `.db` dosyanızı kopyalayın.

---

## 🚀 Çalıştırma

```bash
streamlit run agenticsql.py
```

Tarayıcıda `http://localhost:8501` adresine gidin.

---

## 🔌 Oracle Bağlantısı

AgenticSQL, Oracle Thin Mode kullandığı için ek Oracle Client kurulumu gerektirmez.

1. Sol menüden **Oracle** seçin
2. **Yeni Bağlantı Ekle** ile bağlantı bilgilerini girin
3. **Kaydet ve Bağlan** — bağlantı `Database/oracle_connections.json` dosyasına kaydedilir
4. Sonraki girişlerde **Kayıtlı Bağlantı** listesinden seçebilirsiniz

---

## 🔒 Güvenlik

- `DROP`, `DELETE`, `ALTER` komutları sistem prompt düzeyinde engellenir
- Login ekranı ile yetkisiz erişim önlenir
- Kimlik bilgileri `.env` dosyasında tutulur, kaynak koda dahil edilmez
- Oracle şifreler bellekte tutulur, diske yazılmaz *(oracle_connections.json'a kaydedilir — üretim ortamında şifreleme önerilir)*

---

## 🧪 Testler

```bash
pytest tests/
```

---

## 📄 Lisans

MIT License — ayrıntılar için `LICENSE` dosyasına bakın.
