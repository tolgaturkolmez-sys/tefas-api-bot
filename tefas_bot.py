import json
import time
import io
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
    print("🚀 TEFAS Bot başlatılıyor (Kesintisiz Sayfalama Modu)...")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")
    
    # 🛡️ GÜVENLİK ZIRHI (Takasbank'ın engellememesi için şart)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    fund_map = {}

    try:
        url = "https://www.tefas.gov.tr/tr/fon-verileri?fundType=YAT"
        print(f"🌐 {url} adresine gidiliyor...")
        driver.get(url)

        print("⏳ Sitenin ve tablonun yüklenmesi bekleniyor...")
        time.sleep(5) 
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        sayfa_no = 1
        
        while True:
            print(f"📄 Sayfa {sayfa_no} okunuyor...")
            
            # 1. HTML'i Pandas ile okuyoruz (Uyarıyı önlemek için StringIO kullanıldı)
            html_source = driver.page_source
            dfs = pd.read_html(io.StringIO(html_source), decimal=',', thousands='.')
            
            if not dfs:
                print("❌ Tablo bulunamadı, döngü sonlandırılıyor.")
                break
                
            df = dfs[0]
            
            # Sütunları tespit et
            kod_sutunu = next((col for col in df.columns if 'Kod' in str(col)), None)
            fiyat_sutunu = next((col for col in df.columns if 'Fiyat' in str(col) or 'Değer' in str(col)), None)
            
            # 2. KRİTİK NOKTA: O anki sayfanın İLK fon kodunu kaydediyoruz (AAK, MAC vs.)
            mevcut_ilk_fon = str(df.iloc[0][kod_sutunu]) if kod_sutunu else str(df.iloc[0, 0])
            
            # Verileri havuza ekle
            records = df.to_dict(orient="records")
            for row in records:
                code = row.get(kod_sutunu)
                price = row.get(fiyat_sutunu)

                if pd.notna(code) and pd.notna(price):
                    try:
                        fund_map[str(code).strip()] = float(price)
                    except (ValueError, TypeError):
                        pass
                        
            print(f"✅ Sayfa {sayfa_no} işlendi. Havuzdaki toplam fon: {len(fund_map)}")

            # 3. 'Sonraki' Butonunu Bul
            sonraki_btn = None
            try:
                elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Sonraki')]/ancestor-or-self::button | //*[contains(text(), 'Sonraki')]/ancestor-or-self::a | //*[contains(text(), 'Sonraki')]/ancestor-or-self::li")
                
                for el in elements:
                    if el.is_displayed():
                        class_name = el.get_attribute("class") or ""
                        if el.get_attribute("disabled") or "disabled" in class_name or "p-disabled" in class_name:
                            continue
                        sonraki_btn = el
                        break
            except Exception:
                pass

            if not sonraki_btn:
                print("🛑 Aktif bir 'Sonraki' butonu bulunamadı. (Tüm sayfalar bitti)")
                break

            # 4. Tıklama ve Yeni Sayfayı Doğrulama
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sonraki_btn)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", sonraki_btn)
                
                # İŞTE ÇÖZÜM: Tablonun ilk hücresindeki fon kodu değişene kadar bekle!
                WebDriverWait(driver, 15).until(
                    lambda d: d.find_element(By.CSS_SELECTOR, "tbody tr:first-child td:first-child").text != mevcut_ilk_fon
                )
                time.sleep(0.5) # Tablonun tam render olması için mini bir bekleme
                sayfa_no += 1
                
            except Exception as e:
                print(f"⚠️ Son sayfaya gelindi veya zaman aşımı.")
                break

        # --- DÖNGÜ BİTTİ ---
        if not fund_map:
            print("❌ Hiç fon çekilemedi.")
            exit(1)

        output = {
            "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "fonlar": fund_map
        }

        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"🎉 BİNGO! Toplam {len(fund_map)} adet benzersiz fon başarıyla güncellendi.")

    except Exception as e:
        print(f"❌ Kritik Hata: {e}")
        exit(1)
    finally:
        print("🧹 Tarayıcı temizlenip kapatılıyor...")
        driver.quit()

if __name__ == "__main__":
    update_funds()
