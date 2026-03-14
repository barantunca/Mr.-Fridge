# Mr.Fridge - Görsel Tarama ve Nesne Tanıma Modülü 👁️🍎

Bu proje, kapsamlı bir akıllı buzdolabı sistemi olan **Mr.Fridge** için geliştirilmiş nesne tanıma modülüdür. Kullanıcıların kameraya gösterdiği gıda veya eşyaları anlık olarak tarar, OpenAI (GPT-4o) Vision API kullanarak analiz eder ve nesnenin ne olduğunu Türkçe olarak tanımlar.

Ana projenin bir alt servisi olarak tasarlanmıştır ve bağımsız olarak da test edilebilir bir Tkinter masaüstü arayüzüne sahiptir.

## 🚀 Özellikler

- **Gerçek Zamanlı Görüntü Yakalama:** OpenCV kullanılarak cihaz kamerasından anlık görüntü akışı sağlanır.
- **Akıllı Analiz (GPT-4o Vision):** Yakalanan kareler Base64 formatına çevrilerek OpenAI'ın en gelişmiş çok modlu yapay zeka modeline iletilir.
- **Doğal Türkçe Çıktı:** Sadece basit etiketler değil, nesnenin bağlamına uygun (örn: "Yarım Elma", "Cam Süt Şişesi") doğal Türkçe yanıtlar üretir.
- **Güvenli Yapılandırma:** API anahtarları `.env` dosyası üzerinden okunarak koddan izole edilir ve güvenlik sağlanır.

## 🛠️ Gereksinimler

Sisteminizde **Python 3.x** yüklü olmalıdır. Projenin çalışması için gereken Python kütüphaneleri şunlardır:

- `opencv-python` (Kamera ve görüntü işleme)
- `pillow` (Arayüzde görüntü gösterme)
- `openai` (GPT-4o Vision API iletişimi)
- `python-dotenv` (Çevresel değişkenlerin ve API anahtarının yönetimi)

## 📦 Kurulum

1. Repoyu bilgisayarınıza klonlayın ve klasöre girin:
   ```bash
   git clone [https://github.com/KULLANICI_ADINIZ/mr-fridge-vision-module.git](https://github.com/KULLANICI_ADINIZ/mr-fridge-vision-module.git)
   cd mr-fridge-vision-module
   ```
