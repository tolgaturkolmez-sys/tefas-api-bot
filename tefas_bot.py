from curl_cffi import requests
import json
from datetime import datetime

def update_funds():
    # Yepyeni Takasbank API uç noktası
    url = "https://tefas.takasbank.com.tr/api/statistics/tefas/getFplFonList"
    
    # Modern JSON tabanlı Header'lar
    headers = {
        "Origin": "https://tefas.takasbank.com.tr",
        "Referer": "https://tefas.takasbank.com.tr/tr",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*"
    }
    
    # Payload artık boş bir JSON nesnesi
    payload = {}
    
    try:
        # Gerçek bir Chrome 110 tarayıcısı gibi davranıyoruz
        r = requests.post(url, json=payload, headers=headers, impersonate="chrome110", timeout=30)
        
        if r.status_code != 200:
            print(f"Bağlantı Hatası! HTTP Kodu: {r.status_code}")
            print(f"Yanıt: {r.text[:300]}")
            exit(1)
            
        try:
            response_json = r.json()
            # Yeni yapıda veriler 'data' anahtarı içinde geliyor
            fund_data = response_json.get('data', [])
        except json.decoder.JSONDecodeError:
            print("Veri JSON formatında gelmedi! IP blokajı olabilir.")
            print(f"Yanıt: {r.text[:300]}")
            exit(1)
        
        # 'fonKod' ve fiyat bilgisini alıyoruz (fiyat değişkeninin adını tahmin ederek 'fiyat' veya 'price' deniyoruz)
        fund_map = {}
        for f in fund_data:
            code = f.get('fonKod')
            # Fiyat verisinin adı fiyat, sonFiyat veya price olabilir, güvenli alma:
            price = f.get('fiyat') or f.get('sonFiyat') or f.get('price') 
            
            if code and price is not None:
                try:
                    fund_map[code] = float(price)
                except ValueError:
                    pass # Geçersiz fiyat formatıysa atla
        
        if not fund_map:
            print("Veri boş döndü. Fiyat veya kod anahtarlarının ismi değişmiş olabilir (Örn: 'fiyat' yerine başka bir şey).")
            # Değişken adlarını görmek için ilk öğeyi ekrana basalım
            if fund_data:
                print(f"Örnek Veri Yapısı: {fund_data[0]}")
            exit(1)
            
        output = {
            "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "fonlar": fund_map
        }
        
        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"Operasyon Başarılı! Yeni Takasbank sisteminden {len(fund_map)} adet fon çekildi.")
        
    except Exception as e:
        print(f"Sistem Hatası: {e}")
        exit(1)

if __name__ == "__main__":
    update_funds()
