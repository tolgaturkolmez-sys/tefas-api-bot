from curl_cffi import requests
import json
from datetime import datetime

def update_funds():
    # Bulduğumuz o muazzam ana liste uç noktası
    url = "https://tefas.takasbank.com.tr/api/statistics/tefas/fonGetiriBazliBilgiGetir"
    
    headers = {
        "Origin": "https://tefas.takasbank.com.tr",
        "Referer": "https://tefas.takasbank.com.tr/tr",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*"
    }
    
    # Payload sekmesini göremediğimiz için boş gönderiyoruz (Tüm listeyi ver demektir)
    payload = {}
    
    try:
        print("Takasbank'a Chrome 110 kılığında bağlanılıyor...")
        r = requests.post(url, json=payload, headers=headers, impersonate="chrome110", timeout=30)
        
        if r.status_code != 200:
            print(f"Bağlantı Hatası! HTTP Kodu: {r.status_code}")
            # 500 veya 400 dönerse, Payload kısmına özel bir parametre eklememiz gerekiyordur.
            print(f"Yanıt: {r.text[:300]}")
            exit(1)
            
        try:
            response_json = r.json()
            # Veriler listesi (Ekran görüntüsünde data'nın direkt liste mi yoksa 'data' anahtarı içinde mi olduğunu varsayıyoruz)
            # Eğer doğrudan liste ise response_json'ın kendisi objedir, değilse 'data' veya 'resultList' içindedir.
            
            if isinstance(response_json, list):
                fund_data = response_json
            elif 'data' in response_json:
                fund_data = response_json['data']
            elif 'resultList' in response_json:
                fund_data = response_json['resultList']
            else:
                fund_data = [response_json] # Ne olur ne olmaz
                
        except json.decoder.JSONDecodeError:
            print("Veri JSON formatında gelmedi! Güvenlik duvarına takıldık.")
            exit(1)
        
        fund_map = {}
        for f in fund_data:
            if not isinstance(f, dict):
                continue
                
            code = f.get('fonKodu')
            # Fiyat verisi 'sonFiyat', 'fiyat', veya 'fiyat1' gibi bir isimle gelmiş olabilir
            price = f.get('sonFiyat') or f.get('fiyat') or f.get('guncelFiyat')
            
            if code and price is not None:
                try:
                    fund_map[code] = float(price)
                except ValueError:
                    pass
        
        # Eğer fon kodu bulup fiyat bulamadıysa PM'i uyar
        if not fund_map and len(fund_data) > 0:
            print("HAY AKSİ! Fon kodlarını buldum ama 'Fiyat' verisini bulamadım.")
            print("İşte Takasbank'ın bu pakette bize gönderdiği veri başlıkları:")
            print(list(fund_data[0].keys()))
            exit(1)
            
        if not fund_map:
            print("Veri boş döndü. Payload (gönderilen veri) eksik!")
            exit(1)
            
        output = {
            "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "fonlar": fund_map
        }
        
        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"Zafer! Yeni Takasbank sisteminden {len(fund_map)} adet fonun güncel fiyatı çekildi.")
        
    except Exception as e:
        print(f"Sistem Hatası: {e}")
        exit(1)

if __name__ == "__main__":
    update_funds()
