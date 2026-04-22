from curl_cffi import requests
import json
from datetime import datetime

def update_funds():
    url = "https://www.tefas.gov.tr/api/DB/BindMainIndicators"
    headers = {
        "Origin": "https://www.tefas.gov.tr",
        "Referer": "https://www.tefas.gov.tr/FonKarsilastirma.aspx",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    }
    payload = "fontip=YAT&sfontip=YAT"
    
    try:
        # impersonate="chrome110" parametresi TEFAS güvenlik duvarını "gerçek insan" olduğuna inandırır
        r = requests.post(url, data=payload, headers=headers, impersonate="chrome110", timeout=30)
        
        # Eğer yine de 200 dönmezse veya HTML dönerse hatayı yazdır ki görelim
        if r.status_code != 200:
            print(f"TEFAS Engeli! HTTP Kodu: {r.status_code}")
            print(f"Dönen Yanıt: {r.text[:500]}")
            exit(1)
            
        try:
            data = r.json().get('d', [])
        except json.decoder.JSONDecodeError:
            print("TEFAS JSON yerine HTML döndürdü. IP tamamen banlanmış olabilir.")
            print(f"Dönen Yanıt: {r.text[:500]}")
            exit(1)
        
        fund_map = {f['Fonkodu']: float(f['Fiyat']) for f in data if f.get('Fonkodu')}
        
        if not fund_map:
            print("Veri boş döndü. TEFAS API formatı değiştirmiş olabilir.")
            exit(1)
            
        output = {
            "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "fonlar": fund_map
        }
        
        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"İşlem Başarılı! {len(fund_map)} adet fon çekildi.")
        
    except Exception as e:
        print(f"Beklenmeyen Hata: {e}")
        exit(1)

if __name__ == "__main__":
    update_funds()
