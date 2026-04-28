import os
import glob
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
    print("🚀 TEFAS Bot başlatılıyor (Akıllı CSV İndirme Modu)...")

    # İndirilen dosyanın kaydedileceği yer (kodun çalıştığı mevcut klasör)
    download_dir = os.getcwd()
    
    # Başlamadan önce klasördeki eski .csv dosyalarını temizle
    for f in glob.glob("*.csv"):
        try:
            os.remove(f)
        except:
            pass

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")
    
    # ⚠️ ÇOK KRİTİK: Görünmez Chrome'un dosya indirmesine izin veren ayarlar
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "profile.default_content_settings.popups": 0,
        "safebrowsing.enabled": False
    }
    options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = "https://www.tefas.gov.tr/tr/fon-verileri?fundType=YAT"
        print(f"🌐 {url} adresine gidiliyor...")
        driver.get(url)

        # Tablonun ve butonların ekrana gelmesini bekle
        print("⏳ Sayfanın yüklenmesi bekleniyor...")
        wait = WebDriverWait(driver, 20)
        
        # İçinde "CSV" yazan butonu bul
        csv_button_xpath = "//*[contains(text(), 'CSV')]/ancestor-or-self::button | //button[contains(., 'CSV')]"
        csv_btn = wait.until(EC.element_to_be_clickable((By.XPATH, csv_button_xpath)))
        
        # Ekstra güvenlik payı: JS eventlerinin bağlanması için 2 saniye bekle
        time.sleep(2) 

        print("📥 'CSV' butonuna tıklanıyor...")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", csv_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", csv_btn)

        # İndirme işleminin tamamlanmasını bekle (Maksimum 30 saniye)
        print("⏳ Dosyanın inmesi bekleniyor...")
        csv_file = None
        for _ in range(30):
            files = glob.glob("*.csv")
            if files:
                # Dosya iniyorken uzantısı .crdownload olur, bitince .csv olur
                cr_files = glob.glob("*.crdownload")
                if not cr_files:
                    csv_file = files[0]
                    break
            time.sleep(1)

        if not csv_file:
            print("❌ HATA: CSV dosyası belirtilen sürede indirilemedi.")
            exit(1)

        print(f"✅ Dosya başarıyla indirildi: {csv_file}")
        print("📊 Pandas ile veriler okunup JSON'a çevriliyor...")

        # TEFAS CSV dosyaları genellikle noktalı virgül (;) ile ayrılır ve Türkçe karakter (cp1254/utf-8) kullanır.
        try:
            df = pd.read_csv(csv_file, sep=';', decimal=',', thousands='.', encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(csv_file, sep=';', decimal=',', thousands='.', encoding='cp1254')

        # İndirilen CSV'deki sütun başlıklarını yakala
        kod_sutunu = next((col for col in df.columns if 'Kod' in str(col)), None)
        fiyat_sutunu = next((col for col in df.columns if 'Fiyat' in str(col) or 'Değer' in str(col)), None)

        fund_map = {}
        records = df.to_dict(orient="records")

        for row in records:
            code = row.get(kod_sutunu)
            price = row.get(fiyat_sutunu)

            if pd.notna(code) and pd.notna(price):
                try:
                    fund_map[str(code).strip()] = float(price)
                except (ValueError, TypeError):
                    pass

        if not fund_map:
            print("❌ CSV okundu ama liste boş. Sütun isimleri değişmiş olabilir.")
            exit(1)

        # Mobil uygulamanın beklediği son format
        output = {
            "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "fonlar": fund_map
        }

        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"🎉 BİNGO! Tek hamlede {len(fund_map)} adet fon güncellendi.")

    except Exception as e:
        print(f"❌ Kritik Hata: {e}")
        exit(1)
    finally:
        print("🧹 Temizlik yapılıyor...")
        driver.quit()
        # İndirilen geçici CSV dosyasını çöpe atıyoruz (GitHub deposunda yer kaplamasın)
        for f in glob.glob("*.csv"):
            try:
                os.remove(f)
            except:
                pass

if __name__ == "__main__":
    update_funds()
