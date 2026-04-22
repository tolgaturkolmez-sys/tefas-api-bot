from curl_cffi import requests
import json
from datetime import datetime

def update_funds():
    # KÖK NEDEN ÇÖZÜLDÜ: Doğru klasör /api/funds/ ve POST isteği
    url = "https://tefas.takasbank.com.tr/api/funds/fonGetiriBazliBilgiGetir"
    
    headers = {
        "Origin": "https://tefas.takasbank.com.tr",
        "Referer": "https://tefas.takasbank.com.tr/tr",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*"
    }
    
    # İŞTE BULDUĞUN O SİHİRLİ ŞİFRE (PAYLOAD)
    payload = {
        "basTarih": None,
        "bitTarih": None,
        "calismaTipi": 2,
        "dil": "TR",
        "donemGetiri1a": "1",
        "donemGetiri1y": "1",
        "donemGetiri3a": "1",
        "donemGetiri3y": "1",
        "donemGetiri5y": "1",
        "donemGetiri6a": "1",
        "donemGetiriyb": "1",
        "fonGrubu": None,
        "fonTipi": "YAT",
        "fonTurAciklama": None,
        "fonTurKod": None,
        "getiriOrani": "1",
        "islem": 1,
        "kurucuKodu": None,
        "sfonTurKod": None
    }
    
    try:
        print("Takasbank'a özel şifre (Payload) ile Chrome 110 kılığında bağlanılıyor...")
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
            # Fiyatı güvence altına alıyoruz (Farklı isimlerle gelebilir)
            price = f.get('sonFiyat') or f.get('fiyat') or f.get('guncelFiyat') or f.get('fiyat1')
            
            if code and price is not None:
                try:
                    fund_map[code] = float(price)
                except ValueError:
                    pass
        
        # Eğer tablo fiyat bilgisini içermiyorsa (Sadece getiri yüzdeleri varsa) bizi uyaracak
        if not fund_map and len(fund_data) > 0:
            print("HAY AKSİ! Fon kodlarını buldum ama tablonun içinde 'Fiyat' verisini bulamadım.")
            print("Takasbank'ın bu tabloda bize gönderdiği başlıklar şunlar:")
            print(list(fund_data[0].keys()))
            exit(1)
            
        if not fund_map:
            print("Veri yine boş döndü! Payload doğru ama sistem anlık yanıt vermemiş olabilir.")
            exit(1)
            
        output = {
            "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "fonlar": fund_map
        }
        
        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"BÜYÜK ZAFER! Yeni Takasbank altyapısından tam {len(fund_map)} adet fonun fiyatı çekildi!")
        
    except Exception as e:
        print(f"Sistem Hatası: {e}")
        exit(1)

if __name__ == "__main__":
    update_funds()
