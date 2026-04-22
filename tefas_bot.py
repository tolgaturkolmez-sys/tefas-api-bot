import requests
import json
from datetime import datetime

def update_funds():
    url = "https://www.tefas.gov.tr/api/DB/BindMainIndicators"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.tefas.gov.tr/FonKarsilastirma.aspx"
    }
    payload = "fontip=YAT&sfontip=YAT"
    
    try:
        r = requests.post(url, data=payload, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json().get('d', [])
        
        fund_map = {f['Fonkodu']: float(f['Fiyat']) for f in data if f.get('Fonkodu')}
        
        output = {
            "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "fonlar": fund_map
        }
        
        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print("İşlem Başarılı.")
    except Exception as e:
        print(f"Hata: {e}")
        exit(1)

if __name__ == "__main__":
    update_funds()
