# Son kalite kontrolü

## Otomatik kontroller

- [x] Backend Ruff statik kontrolü
- [x] Backend Ruff format kontrolü
- [x] Backend: 91 pytest testi
- [x] Frontend: 20 Vitest testi
- [x] Frontend ESLint kontrolü
- [x] TypeScript `tsc --noEmit`
- [x] Next.js production build
- [x] Streamlit yerel sunucu ve `/_stcore/health` kontrolü

## Kapsanan kritik davranışlar

- [x] Seed tabanlı demo tekrarlandığında konum, kenar ve enfeksiyon durumları aynı
- [x] GTAD eylemleri yeni/kesilen kenar ve karantina görsel durumlarına dönüşüyor
- [x] Presentation modu sade etiketleri ve sahne görünümünü kullanıyor
- [x] Canlı laboratuvar playback yaşam döngüsü ve kare sınırları korunuyor
- [x] İHA inceleme paneli ağ özelliklerini, risk skorunu ve olay geçmişini doğru hesaplıyor
- [x] Olay merkezi birleşik filtreleri, olay özetini ve UTF-8 dışa aktarımları koruyor
- [x] Deney Merkezi seed doğrulaması, koşu bütçesi ve güven aralığı özetlerini doğru üretiyor
- [x] Karşılaştırma ekranı metrik yönünü, baseline farklarını ve normalize skorları koruyor
- [x] Rapor Merkezi bilimsel bağlamı, Unicode içeriği ve güvenli HTML çıktısını koruyor
- [x] Metodoloji kataloğu çalışma zamanı stratejileri, metrikleri ve GTAD ağırlıklarıyla eşleşiyor
- [x] Hakkında sayfası ürün profili, yol haritası ilerlemesi ve navigasyon kaydıyla doğrulanıyor
- [x] Çalışma alanı paketi kayıpsız geri yükleniyor; şema, boyut ve SHA-256 bütünlüğü doğrulanıyor
- [x] Tasarım token'ları, erişilebilir renk kontrastları ve ortak CSS temeli doğrulanıyor
- [x] Simülasyon ve deney cache'leri tekrar kullanım, izolasyon ve temizleme davranışlarını koruyor
- [x] Ağır Streamlit bölümleri yalnızca seçili görünümde oluşturuluyor
- [x] Beş uçtan uca Streamlit kullanıcı yolculuğu hatasız tamamlanıyor
- [x] Sayfa hata sınırı teknik ayrıntıları gizliyor ve güvenli yeniden deneme sunuyor
- [x] Ortak boş durumlar kullanıcıyı doğru başlangıç ekranına yönlendiriyor
- [x] Streamlit Cloud Python 3.13 kurulumu, genel URL ve bütün sayfa rotaları doğrulandı
- [x] Production npm bağımlılık denetiminde bilinen açık yok
- [x] Hassas dosya, anahtar ve yanlışlıkla teslim edilecek üretim çıktısı taraması temiz
- [x] Scientific modda metrikler, olaylar ve denetim metadata'sı korunuyor
- [x] CSV, Parquet ve manifest deney çıktıları mevcut testlerle doğrulanıyor

## Bilinen bilgi notu

Testlerde görülen tek uyarı, Starlette'in test istemcisindeki AnyIO alias'ına ait
üçüncü taraf bir deprecation uyarısıdır; test sonucu veya uygulama davranışını
etkilemez.

Sistem genelindeki Python 3.14 bu bağımlılık kümesiyle desteklenmez. Proje
metadata'sı 3.10–3.13 aralığını zorunlu kılar; komutlar etkin proje sanal
ortamında çalıştırılmalıdır.
