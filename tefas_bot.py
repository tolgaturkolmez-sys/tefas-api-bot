import requests
import json
import os

def fetch_tefas_data():
    # TEFAS'ın veri çektiği asıl API adresi
    api_url = "https://www.tefas.gov.tr/api/DB/Bind2Container/GetFundData"
    
    # Tarayıcı gibi görünmek için gerekli başlıklar
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    
    # Tüm yatırım fonlarını çeken parametreler
    # Not: offset 0 ve limit 2000 yaparak tüm listeyi tek seferde alıyoruz
    payload = {
        "fundType": "YAT",
        "order[0][column]": "0",
        "order[0][dir]": "asc",
        "start": "0",
        "length": "3000" 
    }

    try:
        print("TEFAS API'sine bağlanılıyor...")
        response = requests.post(api_url, data=payload, headers=headers)
        
        if response.status_code == 200:
            raw_data = response.json()
            # TEFAS API verisi 'data' anahtarı altında döner
            funds_list = raw_data.get("data", [])
            
            if not funds_list:
                print("Hata: API'den veri gelmedi!")
                return

            # JSON dosyasına kaydet
            file_path = 'yatirim_fonlari.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(funds_list, f, ensure_ascii=False, indent=4)
            
            print(f"Başarılı! {len(funds_list)} adet fon '{file_path}' dosyasına kaydedildi.")
        else:
            print(f"API Hatası! Durum Kodu: {response.status_code}")

    except Exception as e:
        print(f"Beklenmedik bir hata oluştu: {e}")

if __name__ == "__main__":
    fetch_tefas_data()
