# SwarmGuard son ürün denetimi

Tarih: 7 Ekim 2026

## Sonuç

Adım 47 tamamlandı. Uygulamanın simülasyon, deney, raporlama, veri taşıma ve
çok sayfalı Streamlit akışları yerel ortamda çalışıyor. Otomatik doğrulama
kapıları geçiyor. Kod, yapılandırma, GitHub teslimi ve genel Streamlit Cloud
yayını doğrulandı. Yol haritasındaki 47 adımın tamamı tamamlandı.

## Geçen kontroller

- Backend: 91 / 91 pytest testi
- Backend: Ruff format ve statik analiz
- Frontend: 20 / 20 Vitest testi
- Frontend: ESLint ve TypeScript kontrolü
- Frontend: Next.js production build
- Streamlit: `/`, `/overview`, `/simulation`, `/workspace`, `/experiments`,
  `/methodology`, `/about` ve `/_stcore/health` rotalarında HTTP 200
- Üretim npm bağımlılık denetimi: bilinen güvenlik açığı yok
- Python bağımlılık bütünlüğü: kırık paket yok
- Hassas dosya taraması: token, anahtar, secrets veya `.env` teslimatı yok
- Cloud paketi: giriş noktası, requirements, tema ve headless ayarları geçerli

Toplam otomatik uygulama testi 111'dir. Streamlit kullanıcı yolculukları bu
toplamın içinde uygulama kabuğu, senaryo-simülasyon-analiz, deney-karşılaştırma-
rapor, çalışma alanı dışa/içe aktarma ve metodoloji/hakkında akışlarını kapsar.

## Denetimde düzeltilen konu

Makinedeki genel `python` komutu 3.14'e işaret ediyor ve mevcut bilimsel
bağımlılık kümesi bu sürümde çalışmıyor. Paket metadata'sı `>=3.10,<3.14`
olarak netleştirildi. Yerel ve Cloud çalıştırma için Python 3.10–3.13 ile proje
sanal ortamı kullanılmalıdır.

## Açık kalanlar

### Yayın durumu

- Kod `https://github.com/dgknylz/swarmguard` deposunun `main` dalındadır.
- Genel uygulama `https://7dtgk27v5yinc3r2ouqkck.streamlit.app` adresindedir.
- Community Cloud soğuk kurulumu Python 3.13 ile tamamlandı ve bütün sayfa
  rotaları dışarıdan HTTP 200 döndürdü.

### Ürün sınırları

- Veriler Streamlit oturum belleğinde tutulur. Sunucu tarafı kalıcı veritabanı,
  kullanıcı hesabı ve çok cihazlı otomatik senkronizasyon yoktur. JSON çalışma
  alanı paketiyle manuel taşıma vardır.
- Büyük Monte Carlo ve ablation işleri eşzamanlı çalışır. Arka plan iş kuyruğu,
  kalıcı sonuç deposu ve kullanıcı tarafından iş iptali yoktur.
- Önbellek tek süreç belleğindedir; birden fazla Cloud instance arasında ortak
  değildir ve yeniden başlatmada silinir.
- 500 düğüm / 10.000 adım yapılandırmaları doğrulanabilir olsa da Community
  Cloud kaynak limitleri altında uçtan uca yük testi yapılmadı.
- Mobil CSS ve klavye odak kuralları bulunur; gerçek telefon matrisi, ekran
  okuyucu ve bağımsız WCAG denetimi yapılmadı.
- Arayüz stili bazı Streamlit `data-testid` seçicilerine bağlıdır; büyük bir
  Streamlit yükseltmesinde görsel regresyon kontrolü gerekir.
- Next.js istemcisi de depoda bulunur fakat yayın hedefi Streamlit'tir. İki
  arayüzün birlikte geliştirilmesi bakım maliyeti yaratır.

### Bilimsel kapsam

- Sonuçlar simülasyon bulgularıdır; gerçek İHA donanımı, RF kanal modeli,
  saha telemetrisi veya donanım-içinde-döngü doğrulaması yoktur.
- SIS modeli düğümlerin yalnızca sağlıklı/enfekte durumlarını temsil eder;
  saldırgan davranışlarının tüm gerçek dünya çeşitliliğini kapsamaz.
- Savunmalar araştırma karşılaştırması içindir; operasyonel otonom karar sistemi
  ya da güvenlik sertifikalı uçuş yazılımı değildir.

## Yayın tamamlanma kanıtı

Adım 46 aşağıdaki üç kanıtla tamamlanmıştır:

1. GitHub `origin` remote'u ve push edilmiş commit,
2. Community Cloud'da başarılı build logu,
3. Dışarıdan açılan genel `https://…streamlit.app` adresinde sağlık ve temel
   kullanıcı yolculuğu kontrolü.
