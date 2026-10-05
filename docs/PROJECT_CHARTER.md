# Proje Sözleşmesi

## Araştırma sorusu

Graf yapısını dikkate alan adaptif topoloji yeniden yapılandırması, dinamik
İHA haberleşme ağlarında SIS tipi bir siber saldırı karşısında ağ
dayanıklılığını temel savunma yöntemlerine göre artırır mı?

## İlk kapsam

- 2B, sınırları belli bir görev alanı
- Sabit sayıda ve sabit hızda hareket eden İHA'lar
- Mesafe tabanlı, yönsüz haberleşme grafı
- SIS yayılım modeli
- Rastgele, degree ve betweenness saldırı başlangıçları
- Savunmasız, rastgele yeniden bağlantı, merkeziyet tabanlı savunma ve GTAD
- Çoklu seed ile eşleştirilmiş Monte Carlo karşılaştırmaları

## Başarı ölçütleri

- Aynı parametreler ve seed aynı sonucu üretmeli.
- Tüm yöntemler aynı başlangıç senaryosu ve rastgelelik planında ölçülmeli.
- Her metrik için ortalama ile birlikte belirsizlik gösterilmeli.
- GTAD yalnızca optimize ettiği metrikle değil; enfeksiyon, bağlantısallık ve
  müdahale maliyetiyle birlikte değerlendirilmelidir.
- Simülasyon motoru kullanıcı arayüzünden bağımsız test edilebilmelidir.

## Temel metrikler

- Enfekte düğüm oranı
- Tepe enfeksiyon oranı
- Toparlanma süresi
- Largest Connected Component oranı
- Global efficiency
- Algebraic connectivity (lambda_2)
- Eklenen/kesilen bağlantı sayısı
- Savunma müdahale maliyeti

## Kapsam dışı: ilk sürüm

- Gerçek uçuş kontrolü veya fiziksel İHA bağlantısı
- 3B aerodinamik uçuş modeli
- Gerçek kriptografik saldırı yürütme
- Makine öğrenmesi tabanlı saldırı tespiti
- Çok kullanıcılı yetkilendirme

