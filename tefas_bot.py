import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def fetch_tefas_data():
    url = "https://www.tefas.gov.tr/tr/fon-verileri?fundType=YAT"
    
    # Chrome'u arkaplanda (headless) çalışması için ayarlıyoruz
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    print("Tarayıcı başlatılıyor ve TEFAS'a bağlanılıyor...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        
        # Tablonun yüklenmesi için bekliyoruz (Maksimum 20 saniye)
        wait = WebDriverWait(driver, 20)
        # Tablonun body kısmının geldiğinden emin oluyoruz
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        print("Tablo yüklendi. 25'li limit kaldırılıyor...")
        
        # Sayfada "Kayıtları Göster" (DataTables length) dropdown'ı varsa onu bulup "Tümü" veya en büyük değeri seçiyoruz
        try:
            # Dropdown elementini bul (Genelde select elementi class'ı veya name'i ile bulunur)
            # Not: Sitenin yapısına göre bu seçici (selector) değişebilir. Genel bir datatable yapısı varsayılmıştır.
            select_element = wait.until(EC.presence_of_element_located((By.XPATH, "//select[contains(@name, 'length')]")))
            select = Select(select_element)
            
            # Seçenekler arasında '-1' (Tümü) veya '100' vb. en büyük değeri seç
            options = [opt.get_attribute("value") for opt in select.options]
            if "-1" in options:
                select.select_by_value("-1")  # 'Tümü' seçeneği
            else:
                select.select_by_index(len(options) - 1) # En sondaki seçeneği (en büyük sayıyı) seç
                
            time.sleep(3) # Tablonun yeniden yüklenmesi için kısa bir bekleme
            print("Tüm veriler sayfaya yüklendi.")
        except Exception as e:
            print("Dropdown bulunamadı veya sayfada farklı bir pagination var. Sayfa sayfa geçiş stratejisi denenebilir.")
            # Eğer dropdown yoksa, Next (İleri) butonuna tıklayarak döngüye giren bir kod da yazılabilir.

        # Tablonun güncel (tüm verileri içeren) HTML kaynağını alıyoruz
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        
        # Tabloyu parse ediyoruz
        table = soup.find('table')
        headers = [th.text.strip() for th in table.find('thead').find_all('th')]
        
        funds_data = []
        rows = table.find('tbody').find_all('tr')
        
        for row in rows:
            cols = row.find_all('td')
            if cols:
                fund = {}
                for i, col in enumerate(cols):
                    # Başlık sayısıyla sütun sayısını eşleştiriyoruz
                    if i < len(headers):
                        fund[headers[i]] = col.text.strip()
                funds_data.append(fund)
        
        print(f"Toplam {len(funds_data)} adet fon verisi çekildi.")
        
        # Veriyi JSON olarak kaydet
        with open('yatırım_fonları.json', 'w', encoding='utf-8') as f:
            json.dump(funds_data, f, ensure_ascii=False, indent=4)
            
        print("Veriler 'yatırım_fonları.json' dosyasına başarıyla kaydedildi.")

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_tefas_data()
