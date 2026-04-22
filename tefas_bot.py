from curl_cffi import requests
import json
from datetime import datetime

def update_funds():
    # KÖK NEDEN ÇÖZÜLDÜ: Takasbank API'si /api/funds/ dizinine taşınmış.
    url = "https://tefas.takasbank.com.tr/api/funds/fonGetiriBazliBilgiGetir"
    
    headers = {
        "Origin": "https://tefas.takasbank.com.tr",
        "Referer": "https://tefas.takasbank.com.tr/tr",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*"
    }
    
    # POST isteği için boş veri paketi (Tüm listeyi getir demek)
    payload = {}
    
    try:
        print("Takasbank API'sine bağlanılıyor (Yeni /api/funds/ dizini)...")
        # impersonate="chrome110" ile güvenlik duvarını (WAF) gerçek bir tarayıcı olduğumuza inandırıyoruz
        r = requests.post(url, json=payload, headers=headers, impersonate="chrome110", timeout=30)
        
        if r.status_code != 200:
            print(f"Bağlantı Hatası! HTTP Kodu: {r.status_code}")
            print(f"Yanıt: {r.text[:300]}")
            exit(1)
            
        try:
            response_json = r.json()
            # Takasbank'ın veri yapısına göre JSON içindeki listeyi buluyoruz
            if isinstance(response_json, list):
                fund_data = response_json
            elif 'data' in response_json:
                fund_data = response_json['data']
            elif 'resultList' in response_json:
                fund_data = response_json['resultList']
            else:
                fund_data = [response_json] 
                
        except json.decoder.JSONDecodeError:
            print("Veri JSON formatında gelmedi! Güvenlik duvarına takıldık.")
            exit(1)
        
        fund_map = {}
        for f in fund_data:
            if not isinstance(f, dict):
                continue
                
            code = f.get('fonKodu')
            # Fiyat verisi farklı isimlendirmelerle gelebilir, garantiye alıyoruz
            price = f.get('sonFiyat') or f.get('fiyat') or f.get('guncelFiyat')
            
            if code and price is not None:
                try:
                    fund_map[code] = float(price)
                except ValueError:
                    pass
        
        # Olası hata ayıklama (Fiyat parametresinin ismini değiştirmişlerse)
        if not fund_map and len(fund_data) > 0:
            print("HAY AKSİ! Fon kodlarını buldum ama 'Fiyat' verisini bulamadım.")
            print("Gelen veri başlıkları:", list(fund_data[0].keys()))
            exit(1)
            
        if not fund_map:
            print("Veri boş döndü. Payload (gönderilen veri) özel bir filtre istiyor olabilir.")
            exit(1)
            
        # JSON formatını hazırlıyoruz
        output = {
            "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "fonlar": fund_map
        }
        
        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"BÜYÜK ZAFER! Yeni Takasbank sunucusundan {len(fund_map)} adet fon başarıyla çekildi.")
        
    except Exception as e:
        print(f"Sistem Hatası: {e}")
        exit(1)

if __name__ == "__main__":
    update_funds()
