# HistorAI - Tarihi Karakter Chatbotu

Tarihi figürlerle etkileşimli sohbet deneyimi sunan bir yapay zeka platformu. Kullanıcılar Fatih Sultan Mehmet, Leonardo da Vinci, Mevlana gibi tarihi kişiliklerle sohbet edebilir, kritik tarihi olaylara yolculuk yapabilir ve kişilik testiyle kendilerine en uygun karakteri keşfedebilir.

**Canlı Demo:** https://btkhackathonproject-hefzbortmg4mxazvlpqgpx.streamlit.app/

---

## Kurulum ve Çalıştırma

### 1. Bağımlılıkları yükleyin
```bash
pip install -r requirements.txt
```

### 2. Ortam değişkenlerini ayarlayın
Repo ana klasörü içindeki `credentials` klasöründe bir `.env` dosyası oluşturun ve `GEMINI_API_KEY` değişkenini ekleyin (değişken adlandırması için örnek `.env` dosyasına bakınız).

### 3. Uygulamayı başlatın
```bash
streamlit run main.py
```

### API Key Alma
Yerel ortamda kendi API key'inizle çalıştırmak isterseniz:

1. [Google AI Studio](https://makersuite.google.com/app/apikey) sayfasına gidin
2. Yeni bir API key oluşturun
3. Oluşturduğunuz key'i `credentials/.env` dosyasına ekleyin

---

## Proje Tanıtımı

HistorAI, yapay zeka teknolojisini tarih eğitimiyle buluşturan interaktif bir öğrenme platformudur. Kullanıcılar tarihi kişiliklerle doğrudan sohbet ederek geçmişi deneyimler, tarihsel bilgiyi ezberlemek yerine yaşayarak öğrenir.

### Ana Özellikler

| Özellik | Açıklama |
|---|---|
| Tarihi Karakterlerle Sohbet | Dönem diline uygun, tarihsel olarak doğrulanmış yanıtlar ve karaktere özel konuşma tarzları |
| Zamanda Yolculuk | İstanbul'un Fethi (1453), Malazgirt Savaşı (1071) gibi olayların içine sinematik atmosferle yolculuk |
| Kişilik Eşleştirme | Big Five kişilik modeline dayalı 5 soruluk test ile kullanıcıya uygun karakter önerisi |
| Sohbet Yönetimi | Otomatik kayıt, kategorizasyon, sabitleme ve akıllı başlık oluşturma |
| Teknik Özetleme | Sohbetlerden akademik standartta, objektif tarihsel bilgi çıkarımı |
| Çoklu Format İndirme | PDF, Word ve JSON formatlarında yazdırılabilir dışa aktarım |

### Kullanılan Teknolojiler

- **Frontend & Backend:** Streamlit, Python, SQLite
- **Yapay Zeka:** Google Gemini 2.5 Flash, özel prompt engineering ile tarihsel doğruluk ve karakter tutarlılığı
- **Dokümantasyon:** ReportLab (PDF), python-docx (Word), JSON

### Eğitsel Yaklaşım

Proje, empati temelli öğrenme ve gamifikasyon unsurlarını (zamanda yolculuk, kişilik testleri) bir araya getirerek tarih, psikoloji ve teknolojiyi kesiştiren bütünsel bir öğrenme deneyimi sunmayı hedefler. İçerikler yalnızca güvenilir kaynaklara dayalı, tarihsel olarak doğrulanmış bilgilerden oluşturulur.

---

## İletişim

- Baykan Nuri Bayçora — baycorabaykan@gmail.com — [LinkedIn](https://www.linkedin.com/in/baykan-nuri-bay%C3%A7ora-17a197285/)
- Alper Durmuş — 092003alper@gmail.com — [LinkedIn](https://www.linkedin.com/in/alperdurmus1/)