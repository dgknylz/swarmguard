# Streamlit yayınlama rehberi

SwarmGuard'ın Streamlit sürümü, FastAPI ve Next.js sunucularına ihtiyaç duymadan
aynı bilimsel simülasyon çekirdeğini tek uygulama içinde çalıştırır.

## Yerelde çalıştırma

Proje kökünde PowerShell ile:

```powershell
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Tarayıcıdan `http://127.0.0.1:8501` adresini açın.

## Streamlit Community Cloud

1. Ön kontrolü çalıştırın:

   ```powershell
   backend\.venv\Scripts\python.exe -m swarmguard.dashboard.deployment .
   ```

2. Çıktı `READY` olduğunda bu `swarmguard` klasörünü bir GitHub deposuna gönderin.
3. Streamlit Community Cloud'da **Create app** seçeneğini açın.
4. Depoyu, branch'i ve giriş dosyası olarak `streamlit_app.py` dosyasını seçin.
5. Yerelde doğrulanan Python sürümüyle aynı sürümü seçin.
6. **Deploy** ile yayını başlatın.

Cloud kurulumu proje kökündeki `requirements.txt` dosyasını otomatik kullanır.
Tema ve sunucu ayarları `.streamlit/config.toml` içindedir. Uygulama gizli
anahtar kullanmadığı için ek bir secrets dosyası gerekmez.

## Dosya sözleşmesi

- `streamlit_app.py`: Cloud giriş noktası
- `requirements.txt`: Cloud bağımlılıkları
- `.streamlit/config.toml`: tema ve headless sunucu ayarları
- `backend/src/swarmguard/dashboard/app.py`: çok sayfalı uygulama kabuğu
- `backend/src/swarmguard/dashboard/navigation.py`: üst navigasyon ve sayfa kayıtları
- `backend/src/swarmguard/presets.py`: tekrarlanabilir demo senaryosu

Gerçek bir genel URL oluşturmak için GitHub ve Streamlit hesabından son yayın
adımının yapılması gerekir; kod tarafı yayına hazırdır.
