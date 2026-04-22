import requests
import json

def get_all_tefas_funds():
    url = "https://www.tefas.gov.tr/api/DB/BindMainIndicators"
    
    # TEFAS'ın beklediği kritik header'lar
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.tefas.gov.tr/FonKarsilastirma.aspx"
    }
    
    # Tüm fon tiplerini kapsayan payload
    payload = {"fontip": "YAT", "sfontip": "YAT"}
    
    try:
        response = requests.post(url, data=payload, headers=headers)
        data = response.json().get('d', [])
        
        # Senin istediğin formata dönüştürme
        fund_dict = {item['Fonkodu']: item['Fiyat'] for item in data}
        
        output = {
            "guncellenme_tarihi": "2026-04-22",
            "fonlar": fund_dict
        }
        
        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"Başarılı! {len(fund_dict)} adet fon güncellendi.")
        
    except Exception as e:
        print(f"Hata: {e}")

get_all_tefas_funds()
