# Demo akışı

Bu akış, projenin yaklaşık 3–4 dakikalık tutarlı bir sunumunu verir.

## Next.js arayüzü

1. FastAPI ve frontend sunucularını README'deki komutlarla açın.
2. `/simulation` sayfasında **Demo yükle** düğmesine basın.
3. **Simülasyonu başlat** ile seed `2025`, 24 İHA ve GTAD senaryosunu çalıştırın.
4. Scientific modda enfeksiyon, GCC, efficiency ve λ₂ zaman serilerini anlatın.
5. Zaman çizelgesini geri alarak camgöbeği yeni bağlantıları, kesikli kaldırılan
   hatları ve karantina halkalarını gösterin.
6. **Sunum modu** ile sade sahne görünümüne geçin.
7. **Deneyler** sayfasında aynı seed kümesiyle savunmaların karşılaştırıldığını
   ve CSV/Parquet/manifest çıktılarını vurgulayın.

## Streamlit arayüzü

1. `streamlit run streamlit_app.py` komutunu çalıştırın.
2. **Hazır demo senaryosu** açık halde **Simülasyonu çalıştır** düğmesine basın.
3. Replay slider ile saldırının yayılımını ve ağ metriklerini gösterin.
4. **Presentation modu** ile grafik araç çubuğunu ve bilimsel ayrıntıları gizleyin.

Senaryo `demo/scenario.json` dosyasında ayrıca makinece okunabilir olarak bulunur.
