import json
import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def fetch_tefas_data():
    url = "https://www.tefas.gov.tr/tr/fon-verileri?fundType=YAT"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu") # GitHub Actions için önemli
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 30)
        
        # Tablonun gelmesini bekle
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#main-table")))
        
        # Sayfalama limitini kaldır (Tümü seçeneği)
        try:
            select_element = driver.find_element(By.NAME, "main-table_length")
            select = Select(select_element)
            select.select_by_value("-1")
            time.sleep(5) # Verilerin yüklenmesi için bekle
        except:
            print("Dropdown bulunamadı, varsayılan liste ile devam ediliyor.")

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', {'id': 'main-table'})
        
        if not table:
            print("Hata: Tablo bulunamadı!")
            return

        headers = [th.text.strip() for th in table.find('thead').find_all('th')]
        funds_data = []
        
        for row in table.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            if len(cols) > 0:
                fund = {headers[i]: cols[i].text.strip() for i in range(len(headers))}
                funds_data.append(fund)
        
        # DOSYA ADINDA TÜRKÇE KARAKTER KULLANMIYORUZ
        file_path = 'yatirim_fonlari.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(funds_data, f, ensure_ascii=False, indent=4)
            
        print(f"Başarılı! {len(funds_data)} fon kaydedildi: {os.path.abspath(file_path)}")

    except Exception as e:
        print(f"Hata oluştu: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_tefas_data()
