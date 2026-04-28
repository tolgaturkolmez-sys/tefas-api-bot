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
    print("🚀 TEFAS Bot başlatılıyor (Anti-Bot + CSV İndirme Modu)...")

    # İndirme klasörünü ayarla ve eski csv kalıntılarını temizle
    download_dir = os.getcwd()
    for f in glob.glob("*.csv"):
        try: os.remove(f)
        except: pass

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")
    
    # 🛡️ ANTI-BOT ZIRHI GERİ GELDİ (GitHub sunucularında engellenmemek için şart)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # 📥 GİZLİ İNDİRME İZİNLERİ
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "profile.default_content_settings.popups": 0,
        "safebrowsing.enabled": False
    }
    options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # JavaScript Navigator kimliğini silerek bot olduğumuzu gizliyoruz
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        url = "https://www.tefas.gov.tr/tr/fon-verileri?fundType=YAT"
        print(f"🌐 {url} adresine gidiliyor...")
        driver.get(url)

        print("⏳ JavaScript'in sayfayı oluşturması bekleniyor (Maks 30 sn)...")
        wait = WebDriverWait(driver, 30)
        
        # 1. Önce Tablonun Gelmesini Bekle (Sayfanın tam yüklendiğinin garantisi)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        print("📊 Tablo ekranda belirdi! CSV butonu aranıyor...")
        
        time.sleep(2) # JS eventlerinin butona tam bağlanması için mini bir mola
        
        # 2. 'CSV' İbaresi Geçen Herhangi Bir Elementi Yakala
        csv_xpath = "//*[contains(text(), 'CSV')] | //a[contains(@href, 'csv')]"
        csv_btn = wait.until(EC.presence_of_element_located((By.XPATH, csv_xpath)))

        print("📥 'CSV' butonuna tıklanıyor...")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", csv_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", csv_btn)

        # 3. İndirmenin Tamamlanmasını Bekle
        print("⏳ Dosyanın inmesi bekleniyor...")
        csv_file = None
        for _ in range(30):
            files = glob.glob("*.csv")
            cr_files = glob.glob("*.crdownload") # Chrome indirme yaparken bu uzantıyı kullanır
            
            # Eğer .csv dosyası var ve .crdownload dosyası (indirme devam etmiyor) yoksa:
            if files and not cr_files:
                csv_file = files[0]
                break
            time.sleep(1)

        if not csv_file:
            print("❌ HATA: CSV dosyası belirtilen sürede indirilemedi.")
            exit(1)

        print(f"✅ Dosya başarıyla yakalandı: {csv_file}")
        print("📊 Pandas ile veriler okunup JSON'a çevriliyor...")

        # TEFAS .csv standartları: noktalı virgül, Türkçe karakter seti
        try:
            df = pd.read_csv(csv_file, sep=';', decimal=',', thousands='.', encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(csv_file, sep=';', decimal=',', thousands='.', encoding='cp1254')

        # Sütun isimleri dinamik aranıyor
        kod_sutunu = next((col for col in df.columns if 'Kod' in str(col)), None)
        fiyat_sutunu = next((col for col in df.columns if 'Fiyat' in str(col) or 'Değer' in str(col)), None)

        fund_map = {}
        records = df.to_dict(orient="records")

        # JSON formatına dönüşüm (Finans Asistanım uyumlu)
        for row in records:
            code = row.get(kod_sutunu)
            price = row.get(fiyat_sutunu)

            if pd.notna(code) and pd.notna(price):
                try:
                    fund_map[str(code).strip()] = float(price)
                except (ValueError, TypeError):
                    pass

        if not fund_map:
            print("❌ CSV okundu ama liste boş. TEFAS formatı değiştirmiş olabilir.")
            exit(1)

        output = {
            "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "fonlar": fund_map
        }

        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"🎉 BİNGO! Tek hamlede {len(fund_map)} adet fon okundu ve JSON'a aktarıldı.")

    except Exception as e:
        print(f"❌ Kritik Hata: {e}")
        print("\n⚠️ TEŞHİS RAPORU: GitHub sunucusunda engellendiysek HTML şöyle gözükür:")
        print(driver.page_source[:1000]) # Hata olursa sayfanın kodunu görelim
        exit(1)
    finally:
        print("🧹 Temizlik yapılıyor...")
        driver.quit()
        # GitHub deposunda çöp bırakmamak için inen .csv'yi siliyoruz
        for f in glob.glob("*.csv"):
            try: os.remove(f)
            except: pass

if __name__ == "__main__":
    update_funds()
