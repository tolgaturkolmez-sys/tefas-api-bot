from curl_cffi import requests
import json
from datetime import datetime

def update_funds():
    # Uç nokta (Endpoint) adresi (Eğer Headers'ta farklıysa burayı güncelle)
    url = "https://tefas.takasbank.com.tr/api/statistics/tefas/fonBilgiGetir"
    
    headers = {
        "Origin": "https://tefas.takasbank.com.tr",
        "Referer": "https://tefas.takasbank.com.tr/tr",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*"
    }
    
    # Şimdilik boş gönderiyoruz. (Eğer hata alırsak Payload sekmesine bakmamız gerekecek)
    payload = {}
    
    try:
        r = requests.post(url, json=payload, headers=headers, impersonate="chrome110", timeout=30)
        
        if r.status_code != 200:
            print(f"Bağlantı Hatası! HTTP Kodu: {r.status_code}")
            print(f"Yanıt: {r.text[:300]}")
            exit(1)
            
        try:
            response_json = r.json()
            # YENİ YAPI: Veriler artık 'resultList' içinde
            fund_data = response_json.get('resultList', [])
        except json.decoder.JSONDecodeError:
            print("Veri JSON formatında gelmedi! IP blokajı olabilir.")
            exit(1)
        
        fund_map = {}
        for f in fund_data:
            # YENİ YAPI: Doğru değişken isimleri
            code = f.get('fonKodu')
            price = f.get('sonFiyat')
            
            if code and price is not None:
                try:
                    fund_map[code] = float(price)
                except ValueError:
                    pass
        
        if not fund_map:
            print("Veri boş döndü. Payload (gönderilen veri) eksik olabilir veya bu uç nokta toplu veri vermiyor olabilir.")
            print(f"Gelen JSON: {response_json}")
            exit(1)
            
        output = {
            "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "fonlar": fund_map
        }
        
        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"Zafer! Yeni Takasbank sisteminden {len(fund_map)} adet fonun FİYAT verisi çekildi.")
        
    except Exception as e:
        print(f"Sistem Hatası: {e}")
        exit(1)

if __name__ == "__main__":
    update_funds()
