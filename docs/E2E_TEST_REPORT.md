# Uçtan Uca Kullanıcı Testi

**Durum:** BAŞARILI · 5/5 kullanıcı yolculuğu

## Kapsam

Bu test paketi Streamlit arayüzünü kullanıcı etkileşimleri üzerinden çalıştırır.
Yalnızca hesaplama fonksiyonlarını değil; form gönderimi, oturum durumu, görünüm
geçişi, grafik üretimi ve dışa aktarma bileşenlerini birlikte doğrular.

## Otomatik kullanıcı yolculukları

1. Uygulama kabuğu açılır; marka, ana sayfa ve sistem durumu görüntülenir.
2. Sekiz İHA ve üç adımlı senaryo formdan çalıştırılır.
3. Canlı ağda UAV-03 seçilir ve düğüm inceleme paneli doğrulanır.
4. Analiz görünümüne geçilir ve Olay ve Saldırı Merkezi açılır.
5. İki seed ve iki yöntemle dört koşuluk Monte Carlo deneyi çalıştırılır.
6. Aynı deney Karşılaştırma Ekranı'nda iki grafikle incelenir.
7. Rapor Merkezi Markdown ve HTML indirme eylemlerini hazırlar.
8. Çalışma alanı SHA-256 kimliğiyle dışa aktarmaya hazırlanır.
9. Metodoloji denklemleri, ürün kapsamı ve tasarım sistemi vitrini açılır.

## Başarı ölçütleri

- Hiçbir yolculukta yakalanmamış Streamlit istisnası oluşmamalıdır.
- Formdan oluşturulan senaryo oturum durumuna doğru aktarılmalıdır.
- Görünmeyen ağır bölümler oluşturulmamalıdır.
- Deney, karşılaştırma ve rapor aynı deney geçmişini kullanmalıdır.
- Dışa aktarma eylemleri kullanıcıya hazır olmalıdır.
- Bilimsel metodoloji ve sorumlu kullanım bilgileri erişilebilir olmalıdır.

## Son doğrulama

- Uygulama kabuğu: başarılı
- Simülasyon → İHA inceleme → olay analizi: başarılı
- Deney → karşılaştırma → rapor: başarılı
- Çalışma alanı dışa aktarma: başarılı
- Metodoloji → ürün kapsamı: başarılı

## Çalıştırma

```powershell
backend\.venv\Scripts\python.exe -m pytest backend/tests/test_user_journey.py -q
```

Tam kalite kapısı için:

```powershell
backend\.venv\Scripts\python.exe -m ruff format --check backend/src backend/tests
backend\.venv\Scripts\python.exe -m ruff check backend/src backend/tests
backend\.venv\Scripts\python.exe -m pytest backend/tests -q
cd frontend
npm test -- --run
npm run lint
npm run typecheck
```
