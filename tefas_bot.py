import requests
import json
from datetime import datetime

def fetch_tefas_data():
    # TEFAS'ın karşılaştırma tablosunu besleyen asıl API endpoint'i
    url = "https://www.tefas.gov.tr/api/DB/BindMainIndicators"
    
    # Tarayıcı gibi görünmek için bu header'lar şart
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://www.tefas.gov.tr",
        "Referer": "https://www.tefas.gov.tr/FonKarsilastirma.aspx",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    # Tüm yatırım fonlarını (YAT) çekmek için gereken parametre
    payload = "fontip=YAT&sfontip=YAT"
    
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=30)
        response.raise_for_status() # Hata varsa yakala
        
        # 'd' anahtarı içindeki veriyi al (TEFAS formatı böyledir)
        raw_data = response.json().get('d', [])
        
        # Veriyi senin istediğin {"KOD": FIYAT} formatına dönüştür
        funds = {}
        for item in raw_data:
            code = item.get('Fonkodu')
            price = item.get('Fiyat')
            if code and price is not None:
                # Fiyatı float'a çeviriyoruz (Uygulama tarafında hesaplama yapabilmen için)
                funds[code] = float(price)
        
        # Çıktı formatını hazırla
        result = {
            "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "fonlar": funds
        }
        
        # JSON dosyasını kaydet
        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        print(f"Başarılı: {len(funds)} fon verisi güncellendi.")
        
    except Exception as e:
        print(f"Hata Oluştu: {e}")
        exit(1)

if __name__ == "__main__":
    fetch_tefas_data()
