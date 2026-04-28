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
    print("🚀 TEFAS Bot başlatılıyor (Selenium Anti-Bot Modu)...")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")
    
    # 🛡️ ANTI-BOT ÖNLEMLERİ (Burası kritik)
    # 1. Gerçek bir tarayıcı gibi görünmek için güncel bir User-Agent ekliyoruz
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    
    # 2. Selenium'un kendini ele veren 'otomasyon' bayraklarını gizliyoruz
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # 3. JavaScript seviyesinde navigator.webdriver değişkenini silerek bot olduğumuzu gizliyoruz
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        url = "https://www.tefas.gov.tr/tr/fon-verileri?fundType=YAT"
        print(f"🌐 {url} adresine gidiliyor...")
        driver.get(url)

        # GitHub sunucuları daha yavaş render alabilir, bekleme süresini 5 saniyeye çıkardık
        print("⏳ JavaScript'in tabloyu oluşturması bekleniyor (Maks 30 sn)...")
        time.sleep(5) 

        # Tabloyu arama süresini 30 saniyeye esnettik
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        print("📊 Tablo tespit edildi! Pandas ile veriler okunuyor...")

        dfs = pd.read_html(driver.page_source, decimal=',', thousands='.')

        if not dfs:
            print("❌ Sayfada tablo HTML tag'i bulunamadı.")
            exit(1)

        df = dfs[0] 
        kod_sutunu = next((col for col in df.columns if 'Kod' in str(col)), None)
        fiyat_sutunu = next((col for col in df.columns if 'Fiyat' in str(col) or 'Değer' in str(col)), None)

        fund_map = {}
        records = df.to_dict(orient="records")

        for row in records:
            code = row.get(kod_sutunu) if kod_sutunu else row.get('Fon Kodu')
            price = row.get(fiyat_sutunu) if fiyat_sutunu else row.get('Fiyat')

            if pd.notna(code) and pd.notna(price):
                try:
                    fund_map[str(code).strip()] = float(price)
                except (ValueError, TypeError):
                    pass

        if not fund_map:
            print("❌ Veriler işlenirken hata oluştu veya liste tamamen boş geldi.")
            exit(1)

        output = {
            "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "fonlar": fund_map
        }

        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"✅ BAŞARILI! {len(fund_map)} adet fonun fiyatı güncellendi.")

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        print("\n⚠️ TEŞHİS RAPORU:")
        print("GitHub sunucusu tabloyu göremedi. Ekranda görünen sayfanın HTML kodları aşağıdadır:")
        # Eğer Cloudflare engelliyorsa veya bakım varsa, kaynak kodunda "Cloudflare" veya "Access Denied" yazar.
        # Bu sayede sorunun kaynağını net görebiliriz.
        print(driver.page_source[:1500]) 
        exit(1)
    finally:
        print("🧹 Tarayıcı temizlenip kapatılıyor...")
        driver.quit()

if __name__ == "__main__":
    update_funds()
