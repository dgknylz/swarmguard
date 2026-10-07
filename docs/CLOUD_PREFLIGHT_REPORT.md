# Streamlit Community Cloud Ön Kontrol Raporu

## Durum

**Yayın başarılı · Genel URL doğrulandı**

Yerel uygulama, Cloud dosya sözleşmesi ve GitHub teslimi doğrulandı. `main` dalı
`https://github.com/dgknylz/swarmguard` deposuna gönderildi. Uygulama Python
3.13 ile `https://7dtgk27v5yinc3r2ouqkck.streamlit.app` adresinde çalışıyor.

## Geçen kontroller

- `streamlit_app.py` kök giriş noktası mevcut ve dashboard'u başlatıyor.
- Kök `requirements.txt`, `backend[dashboard]` bağımlılık grubunu kuruyor.
- `.streamlit/config.toml` tema ve headless sunucu ayarlarını içeriyor.
- Yerel Python 3.10, projenin desteklediği 3.10–3.13 aralığında.
- Uygulama secrets dosyası veya harici gizli anahtar gerektirmiyor.
- Altı Streamlit rotası yerelde HTTP 200 döndürüyor.
- 91 backend ve 20 frontend testi geçiyor.
- Next.js production build başarıyla tamamlanıyor.

## Cloud doğrulaması

- Ana sayfa, Simülasyon, Çalışma Alanı, Deneyler, Metodoloji, Hakkında ve sağlık
  rotaları dışarıdan HTTP 200 döndürüyor.
- İlk kurulumda seçilen Python 3.14, `pyarrow 21` paketini kaynaktan derleyemedi.
  Cloud çalışma zamanı proje sözleşmesiyle uyumlu Python 3.13'e alınarak sorun
  giderildi.

## Otomatik kontrol komutu

```powershell
backend\.venv\Scripts\python.exe -m swarmguard.dashboard.deployment .
```

Güncel çıktı `READY` durumundadır ve genel yayın doğrulanmıştır.
