import json
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def update_funds():
    print("🚀 TEFAS Bot başlatılıyor (Selenium Tarayıcı Modu)...")

    # GitHub Actions ortamında sorunsuz çalışması için gerekli Chrome ayarları
    options = Options()
    options.add_argument("--headless=new") # Tarayıcıyı arka planda gizli çalıştır
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")

    # webdriver-manager sayesinde ChromeDriver sürüm uyumsuzluğu yaşanmaz
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Hedef yeni nesil TEFAS sayfası
        url = "https://www.tefas.gov.tr/tr/fon-verileri?fundType=YAT"
        print(f"🌐 {url} adresine gidiliyor...")
        driver.get(url)

        print("⏳ JavaScript'in tabloyu oluşturması bekleniyor...")
        time.sleep(3) # Sayfanın iskeletinin oturması için kısa bekleme

        # HTML içinde tablonun belirmesini bekle (Maksimum 20 sn)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        print("📊 Tablo tespit edildi! Pandas kütüphanesi ile veriler okunuyor...")

        # Pandas ile HTML'den tabloyu çek (Ondalık için virgül, binlik için nokta ayarı)
        dfs = pd.read_html(driver.page_source, decimal=',', thousands='.')

        if not dfs:
            print("❌ Sayfada tablo bulunamadı. Yapı değişmiş olabilir.")
            exit(1)

        df = dfs[0] # İlk tabloyu al
        print(f"🔎 Tespit edilen sütunlar: {df.columns.tolist()}")

        # Sütun isimleri TEFAS tarafından değiştirilse bile yakalamak için dinamik arama
        kod_sutunu = next((col for col in df.columns if 'Kod' in str(col)), None)
        fiyat_sutunu = next((col for col in df.columns if 'Fiyat' in str(col) or 'Değer' in str(col)), None)

        fund_map = {}
        records = df.to_dict(orient="records")

        # Finans Asistanım uygulamasının beklediği formata (Sözlük/Map) dönüştürüyoruz
        for row in records:
            code = row.get(kod_sutunu) if kod_sutunu else row.get('Fon Kodu')
            price = row.get(fiyat_sutunu) if fiyat_sutunu else row.get('Fiyat')

            # Pandas'ın boş bıraktığı verileri atla
            if pd.notna(code) and pd.notna(price):
                try:
                    # Kodu temizle, fiyatı float yap
                    fund_map[str(code).strip()] = float(price)
                except (ValueError, TypeError):
                    pass

        if not fund_map:
            print("❌ Veriler işlenirken hata oluştu veya liste tamamen boş geldi.")
            exit(1)

        # Mobil uygulama için JSON şablonunu oluştur
        output = {
            "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "fonlar": fund_map
        }

        # JSON dosyasını oluştur (GitHub Actions bu dosyayı commit edecek)
        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"✅ BAŞARILI! {len(fund_map)} adet fonun fiyatı güncellendi ve yatirim_fonlari.json dosyasına yazıldı.")

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        exit(1)
    finally:
        # RAM sızıntısını önlemek için tarayıcıyı kesinlikle kapat
        print("🧹 Tarayıcı temizlenip kapatılıyor...")
        driver.quit()

if __name__ == "__main__":
    update_funds()
