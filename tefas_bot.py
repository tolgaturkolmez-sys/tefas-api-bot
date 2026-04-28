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
    print("🚀 TEFAS Bot başlatılıyor (Tam Yetkili CSV İndirme Modu)...")

    # ÇÖZÜM 1: İndirme klasörünü kesin ve mutlak (absolute) yol olarak belirliyoruz
    download_dir = os.path.abspath(os.getcwd())
    
    # Eski csv kalıntılarını temizle
    for f in glob.glob("*.csv"):
        try: os.remove(f)
        except: pass

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")
    
    # Anti-Bot Zırhı
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # ÇÖZÜM 2: Headless modda indirmeye izin veren en katı ayarlar
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True, # Chrome'un dosyayı virüs sanıp engellemesini önler
        "profile.default_content_settings.popups": 0
    }
    options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # ÇÖZÜM 3: Chrome DevTools Protocol (CDP) ile arka planda indirme kilidini zorla açıyoruz
    driver.execute_cdp_cmd('Page.setDownloadBehavior', {
        'behavior': 'allow',
        'downloadPath': download_dir
    })
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        url = "https://www.tefas.gov.tr/tr/fon-verileri?fundType=YAT"
        print(f"🌐 {url} adresine gidiliyor...")
        driver.get(url)

        print("⏳ Sayfanın tam yüklenmesi bekleniyor...")
        wait = WebDriverWait(driver, 30)
        
        # Tablo belirene kadar bekle
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        print("📊 Tablo ekranda belirdi! CSV butonu aranıyor...")
        
        time.sleep(3) # JavaScript butonlarının tamamen aktifleşmesi için kısa bir mola
        
        # CSV butonunu bul ve bekle
        csv_xpath = "//*[contains(text(), 'CSV')]/ancestor-or-self::button"
        csv_btn = wait.until(EC.element_to_be_clickable((By.XPATH, csv_xpath)))

        print("📥 'CSV' butonuna tıklanıyor...")
        # JavaScript ile tıklama bazen event'i tetiklemez, standart Selenium click deniyoruz önce
        try:
            csv_btn.click()
        except:
            driver.execute_script("arguments[0].click();", csv_btn)

        # İndirmenin tamamlanmasını bekle
        print("⏳ Dosyanın sunucuya kaydedilmesi bekleniyor...")
        csv_file = None
        for _ in range(40): # Süreyi 40 saniyeye çıkardık (GitHub bazen yavaş indirebilir)
            files = glob.glob("*.csv")
            cr_files = glob.glob("*.crdownload") 
            
            if files and not cr_files:
                csv_file = files[0]
                break
            time.sleep(1)

        if not csv_file:
            print("❌ HATA: CSV dosyası indirilemedi. Chrome izin vermemiş olabilir.")
            exit(1)

        print(f"✅ Dosya başarıyla yakalandı: {csv_file}")
        print("📊 Pandas ile veriler JSON'a dönüştürülüyor...")

        try:
            df = pd.read_csv(csv_file, sep=';', decimal=',', thousands='.', encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(csv_file, sep=';', decimal=',', thousands='.', encoding='cp1254')

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
            print("❌ CSV listesi boş. TEFAS formatı değiştirmiş olabilir.")
            exit(1)

        output = {
            "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "fonlar": fund_map
        }

        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"🎉 BİNGO! İndirilen CSV'den {len(fund_map)} adet fon okundu ve JSON'a aktarıldı.")

    except Exception as e:
        print(f"❌ Kritik Hata: {e}")
        exit(1)
    finally:
        print("🧹 Temizlik yapılıyor...")
        driver.quit()
        for f in glob.glob("*.csv"):
            try: os.remove(f)
            except: pass

if __name__ == "__main__":
    update_funds()
