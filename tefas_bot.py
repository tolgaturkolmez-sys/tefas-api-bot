from curl_cffi import requests
import json
from datetime import datetime

def update_funds():
    # URL yeni Takasbank domainine güncellendi
    url = "https://tefas.takasbank.com.tr/api/DB/BindMainIndicators"
    
    headers = {
        "Origin": "https://tefas.takasbank.com.tr",
        "Referer": "https://tefas.takasbank.com.tr/tr",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    }
    
    payload = "fontip=YAT&sfontip=YAT"
    
    try:
        r = requests.post(url, data=payload, headers=headers, impersonate="chrome110", timeout=30)
        
        if r.status_code != 200:
            print(f"Bağlantı Hatası! HTTP Kodu: {r.status_code}")
            print(f"Dönen Yanıt: {r.text[:500]}")
            exit(1)
            
        try:
            data = r.json().get('d', [])
        except json.decoder.JSONDecodeError:
            print("Veri JSON formatında gelmedi. API adresi değişmiş olabilir.")
            print(f"Dönen Yanıt: {r.text[:500]}")
            exit(1)
        
        fund_map = {f['Fonkodu']: float(f['Fiyat']) for f in data if f.get('Fonkodu')}
        
        if not fund_map:
            print("Veri boş döndü. Sorgu parametreleri değişmiş olabilir.")
            exit(1)
            
        output = {
            "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "fonlar": fund_map
        }
        
        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"İşlem Başarılı! Takasbank'tan {len(fund_map)} adet fon çekildi.")
        
    except Exception as e:
        print(f"Beklenmeyen Hata: {e}")
        exit(1)

if __name__ == "__main__":
    update_funds()
