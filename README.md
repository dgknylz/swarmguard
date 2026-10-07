# SwarmGuard

SwarmGuard, dinamik İHA haberleşme ağlarında siber saldırı yayılımını
incelemek ve adaptif topoloji savunmalarını karşılaştırmak için geliştirilen
bir araştırma ve görselleştirme platformudur.

## Şu anki durum: 46 / 47 adım tamamlandı

Son ürün kontrolü tamamlandı. Kod GitHub'daki `dgknylz/swarmguard` deposuna
gönderildi ve yayın paketi hazırdır; yalnızca genel `streamlit.app` adresinin
oluşturulup doğrulanması beklemektedir.

Bilimsel simülasyon çekirdeği şunları içerir:

- Seed ile tamamen tekrarlanabilir 2B İHA konumları ve hareketi
- Haberleşme menziline göre dinamik NetworkX grafı
- Senkron SIS saldırı yayılımı
- Rastgele, degree ve betweenness tabanlı saldırı başlangıcı
- Enfeksiyon, GCC, global efficiency ve algebraic connectivity metrikleri
- Temel doğruluk ve tekrarlanabilirlik testleri

FastAPI katmanı ile simülasyon oluşturma, durum sorgulama, kontrol ve canlı
WebSocket kare aktarımı eklenmiştir. Next.js uygulaması, responsive tasarım
sistemi, çalışma sayfaları, tip güvenli REST istemcisi, doğrulamalı WebSocket
istemcisi ve Zustand oturum deposu hazırdır.

Canlı çalışma alanı gerçek API'ye bağlanmıştır: kullanıcı parametreleri
değiştirebilir, simülasyonu başlatıp duraklatabilir, devam ettirebilir veya
durdurabilir. WebSocket kareleri React Flow ağına, olay günlüğüne, anlık metrik
kartlarına ve Plotly zaman serilerine aktarılır.

Olay günlüğü olay türü ve İHA bazında filtrelenebilir; kayıtlar CSV veya JSON
olarak dışa aktarılabilir. Bir olaya tıklamak, geçmiş kareyi ve ilgili İHA'yı
açar. Replay sistemi slider, ileri/geri, oynat/duraklat, hız seçimi ve canlı
görünüme dönüş kontrolleriyle simülasyon geçmişini bağımsız olarak oynatır.

Yeni ve kesilen bağlantılar ile karantinaya alınan düğümler ayrı animasyonlarla
gösterilir. Scientific modu bütün denetim ve metrikleri, Presentation modu ise
sunum için sadeleştirilmiş sahne görünümünü sunar. Tek tıkla yüklenen sabit seed'li
demo senaryosu iki modda da kullanılabilir.

Savunma algoritmaları `observe -> decide -> apply -> report` yaşam döngüsünü
uygulayan ortak bir sözleşmeye bağlanmıştır. `none` referansına ek olarak seed
tabanlı rastgele yeniden bağlantı ve merkeziyet tabanlı karantina uygulanmıştır.
GTAD gözlem katmanı; enfeksiyon durumu, enfekte komşu oranı, derece ve
betweenness bileşenlerinden normalize edilmiş bir risk skoru üretir. Sağlıklı
düğümler arasındaki eksik bağlantılar aday olarak üretilir ve bağlantısallık
kazanımı (%50), güvenlik (%30) ve mesafe verimi (%20) bileşenleriyle puanlanır.
Menzil, dinamik azami derece ve müdahale bütçesi kısıtlarını geçen en yüksek
puanlı bağlantılar uygulanır. Aday, eleme, skor ve seçim sonuçları her karede
denetlenebilir metadata olarak raporlanır.

Deney katmanı GTAD ağırlıklarını tam model, bağlantısallıksız, güvenliksiz ve
mesafesiz varyantlarla ablation koşularına ayırır. Monte Carlo motoru seçilen
savunmaları aynı seed kümesiyle çalıştırır; koşu metriklerini yöntem bazında
özetler ve her savunmayı aynı seed'in savunmasız baseline sonucu ile eşleştirir.
Deneyler API'den veya aktif Deneyler ekranından çalıştırılabilir.

Yöntem ortalamaları ve eşleştirilmiş seed farkları iki taraflı Student-t yöntemiyle
%95 güven aralığı içerir. Tam koşu tablosu UTF-8 CSV veya sıkıştırılmış Parquet
olarak indirilebilir. Her deney; senaryo, seed kümesi, yöntemler, metrikler,
eşleştirme anahtarı ve yazılım sürümünü içeren SHA-256 parmak izli bir JSON
manifesti üretir. Aynı deney tasarımı aynı kimliği ve manifesti üretir.

## Kurulum

Python 3.10–3.13 önerilir. Proje ortamı, sistemdeki diğer Python paketlerinden
etkilenmemesi için sanal ortamda çalıştırılmalıdır.

```powershell
cd backend
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
python -m swarmguard.demo
python -m uvicorn swarmguard.api.app:app --reload
```

API çalıştığında etkileşimli dokümantasyon `http://127.0.0.1:8000/docs`
adresindedir.

Frontend ayrı bir terminalde çalıştırılır:

```powershell
cd frontend
Copy-Item .env.example .env.local
npm install
npm run dev
```

Uygulama `http://127.0.0.1:3000` adresinde açılır.

### Streamlit sürümü

API veya Node.js kurmadan tek uygulama olarak çalıştırmak için proje kökünde:

```powershell
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Uygulama `http://127.0.0.1:8501` adresinde açılır. Streamlit sürümü
Genel Bakış, Simülasyon, Çalışma Alanı, Deneyler, Metodoloji ve Hakkında
sayfalarından oluşan yatay
bir web navigasyonu kullanır. Simülasyon ayarları sol panelde değil, sayfa içindeki
sekmede bulunur. Community Cloud kurulum
adımları [docs/STREAMLIT_DEPLOYMENT.md](docs/STREAMLIT_DEPLOYMENT.md), hazır
sunum akışı ise [docs/DEMO.md](docs/DEMO.md) içindedir.

Ortak uygulama kabuğu; SwarmGuard marka alanı, üst navigasyon,
sistem durumu, aktif senaryo özeti, ortak sayfa başlığı ve sürüm footer'ını
bütün Streamlit sayfalarında tutarlı biçimde gösterir.

Command Center ana sayfası; proje amacını anlatan hero alanı, doğrulama ve
yayın durumu, uçtan uca araştırma akışı, platform modülleri ve son simülasyon
özetini tek bir responsive web sayfasında birleştirir.

Senaryo Oluşturucu; sürü boyutu, görev alanı, hareket, SIS saldırı modeli,
saldırı başlangıcı ve savunma kısıtlarını kapsayan tam yapılandırmayı sayfa
içinde sunar. Koşudan önce beklenen derece, saldırı baskısı, hesap yükü ve
risk uyarıları otomatik hesaplanır.

Hazır Senaryo Kütüphanesi; GTAD dengeli demo, hızlı salgın, kırılgan
haberleşme, yoğun sürü, kritik düğüm karantinası, savunmasız baseline ve
hareketlilik stresi profillerini sunar. Her profil sabit seed, açıklama ve tam
simülasyon yapılandırması içerir; seçildiğinde formu otomatik doldurur.

Canlı Simülasyon Laboratuvarı; başlatma, duraklatma, devam ettirme, durdurma,
başa dönme, kare kare ilerleme ve 0.5×–4× akış hızı kontrollerini sunar.
Streamlit fragment akışı yalnızca canlı sahneyi yeniler; durum, kare, zaman,
savunma algoritması ve ağ metrikleri operasyon telemetrisi olarak gösterilir.

İHA İnceleme Paneli, ağ grafiğinden veya arama alanından seçilen düğümün
konumunu, sağlık ve karantina durumunu, derece ve enfekte komşu oranını,
betweenness merkeziyetini ve GTAD risk skorunu gösterir. Komşu listesi ile
düğüme özel olay geçmişi, seçili simülasyon karesine göre birlikte güncellenir.

Olay ve Saldırı Merkezi bütün simülasyon geçmişini saldırı, savunma ve sağlık
kategorilerinde birleştirir. Olay türü, İHA ve zaman aralığı filtreleri; özet
göstergeler, kategori zaman çizelgesi ve ayrıntı kartıyla birlikte çalışır.
Seçili olay tek tıkla canlı ağdaki ilgili kare ve İHA üzerinde açılabilir;
filtrelenmiş kayıtlar CSV veya JSON olarak indirilebilir.

Deney Merkezi, aktif senaryoyu Monte Carlo veya GTAD ablation tasarımına
dönüştürür. Kullanıcı savunma yöntemlerini ve eşleştirilmiş seed kümesini seçer;
koşu bütçesi başlamadan önce hesaplanır. Tamamlanan deneyler oturum geçmişinde
tutulur; yöntem ortalamaları ve %95 Student-t güven aralıkları grafik ve tabloyla
sunulur. Ham koşular CSV/Parquet, tekrarlanabilir deney tanımı JSON manifesti
olarak indirilebilir.

Karşılaştırma Ekranı, tamamlanan bir deneyde yöntemleri seçilen başarı metriğinin
yönüne göre sıralar. Ortalama ve %95 güven aralığı, baseline'a göre eşleştirilmiş
seed farkı, seed bazlı sonuç eğrisi ve yedi metrikten oluşan normalize performans
matrisi birlikte sunulur. Monte Carlo deneylerinde savunmasız yöntem, GTAD
ablation deneylerinde tam model otomatik baseline olarak kullanılır.

Rapor Merkezi; deney özeti, senaryo parametreleri, yöntem ortalamaları, baseline'a
göre eşleştirilmiş farklar ve tekrarlanabilirlik kimliğini paylaşılabilir bir
araştırma çıktısında birleştirir. Rapor başlığı, hazırlayan ve araştırmacı notu
arayüzden düzenlenebilir. UTF-8 Markdown çıktısı düzenlenebilir; bağımsız HTML
çıktısı tarayıcıda açılabilir ve yazdırma menüsünden PDF olarak kaydedilebilir.

Metodoloji ve Algoritmalar sayfası; dinamik ağ ve hareket modelini, senkron SIS
denklemlerini, saldırı başlangıçlarını ve ortak savunma yaşam döngüsünü açıklar.
GTAD düğüm riski, bağlantı aday puanı ve uygulanabilirlik kısıtları gerçek kod
ağırlıklarıyla belgelenir. Metrik sözlüğü, eşleştirilmiş deney protokolü,
Student-t güven aralığı, ablation varyantları ve model sınırlamaları ayrı
bölümlerde sunulur.

Hakkında sayfası projenin araştırma problemini, ürün amacını, temel yeteneklerini
ve dört katmanlı mimarisini dışarıdan gelen kullanıcılar için açıklar. Tasarım
ilkeleri, hedef kullanıcılar, yol haritası ilerlemesi ve sorumlu kullanım sınırları
aynı kurumsal ürün görünümünde sunulur.

Çalışma Alanı sayfası aktif senaryoyu, bütün simülasyon karelerini, olayları,
deney geçmişini ve seçili analiz bağlamını taşınabilir bir UTF-8 JSON paketine
dönüştürür. Paketler 1.0 şema sürümü ve SHA-256 bütünlük imzasıyla doğrulanır;
başka bir tarayıcı veya oturumda yüklenerek replay ve deney geçmişiyle birlikte
kaldığı yerden devam edilebilir. Geçersiz, değiştirilmiş veya 25 MB sınırını aşan
dosyalar uygulanmadan reddedilir.

Profesyonel tasarım sistemi; renk, tipografi, boşluk, köşe, gölge ve durum
tonlarını merkezi token sözleşmesinde birleştirir. Üst navigasyon, butonlar,
formlar, tablolar, metrikler, uyarılar ve açılır paneller ortak etkileşim dilini
kullanır. Klavye odak göstergeleri, WCAG uyumlu temel metin kontrastları,
azaltılmış hareket tercihi ve mobil kırılım kuralları uygulama genelinde
tanımlıdır. Canlı token ve bileşen vitrini Hakkında sayfasında bulunur.

Performans katmanı aynı yapılandırmaya ait simülasyonları, Monte Carlo koşularını
ve GTAD ablation sonuçlarını sınırlı bellek önbelleğinde tekrar kullanır. Deney
sonuçları oturumlara derin kopyayla verildiği için cache verisi kullanıcı
değişikliklerinden etkilenmez. Simülasyon ve Deneyler sayfalarındaki görünüm
seçiciler yalnızca açık bölümü üretir; görünmeyen ağ, olay, karşılaştırma ve rapor
grafikleri artık her Streamlit yeniden çalıştırmasında hesaplanmaz.

Uçtan uca kullanıcı testleri; uygulama kabuğunu, formdan senaryo çalıştırmayı,
canlı ağda İHA seçimini, olay analizini, Monte Carlo deneyini, karşılaştırmayı,
rapor indirmelerini, çalışma alanı paylaşımını ve bilimsel referans sayfalarını
gerçek Streamlit bileşen etkileşimleriyle doğrular. Ayrıntılı kapsam ve çalıştırma
komutları [docs/E2E_TEST_REPORT.md](docs/E2E_TEST_REPORT.md) içindedir.

Hata ve boş durum yönetimi bütün sayfaları ortak bir güvenlik sınırına alır.
Beklenmeyen arızalarda teknik ayrıntılar ziyaretçiye sızdırılmaz; oturum verileri
korunur ve yeniden deneme yolu sunulur. Deney, rapor ve çalışma alanı gibi henüz
verisi olmayan bölümler kullanıcıyı doğru başlangıç adımına yönlendirir.

Streamlit Cloud ön kontrolü giriş noktası, bağımlılıklar, tema/sunucu ayarları,
Python sürümü, secrets durumu ve Git teslim sözleşmesini otomatik denetler. Kod,
yerel çalışma zamanı ve GitHub teslimi hazırdır; geriye Community Cloud'da genel
URL'nin oluşturulup test edilmesi kalmıştır. Güncel durum
[docs/CLOUD_PREFLIGHT_REPORT.md](docs/CLOUD_PREFLIGHT_REPORT.md) içindedir.

Son ürün denetiminin geçen kontrolleri, çevre notları ve dürüst kapsam eksikleri
[docs/FINAL_PRODUCT_AUDIT.md](docs/FINAL_PRODUCT_AUDIT.md) içinde kayıtlıdır.

## Bilimsel model

İki İHA arasındaki Öklid mesafesi haberleşme menzilinden küçük veya eşitse
aralarında bir kenar kurulur. Sağlıklı bir düğümün `k` enfekte komşusu varsa
bir zaman adımındaki enfekte olma olasılığı:

```text
P(S -> I) = 1 - (1 - beta)^k
```

Enfekte bir düğüm ise her adımda `gamma` olasılığıyla iyileşir. Durum
geçişleri aynı zaman adımının başlangıcındaki ağ ve enfeksiyon durumundan
senkron olarak hesaplanır.

## Doğrulama

- Backend: 91 test
- Frontend: 20 test
- Ruff, ESLint ve TypeScript kontrolleri
- Next.js production build
- Streamlit başlatma ve sağlık kontrolü

Ayrıntılı son kontrol listesi [docs/QA_CHECKLIST.md](docs/QA_CHECKLIST.md)
içindedir.
