from curl_cffi import requests
import json
from datetime import datetime

def update_funds():
    # Yeni Takasbank API uç noktası
    url = "https://tefas.gov.tr/api/funds/fonGnlBlgSiraliGetir"
    
    # Bugünün tarihini API'nin istediği formatta (YYYYMMDD) alıyoruz
    today_str = datetime.now().strftime("%Y%m%d")
    
    headers = {
        "Origin": "https://tefas.gov.tr",
        "Referer": "https://tefas.gov.tr/tr",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*"
    }
    
    # Görüntüden aldığımız Payload'u "bitSira: 3000" ile güçlendiriyoruz
    payload = {
        "fonTipi": "YAT",
        "fonKodu": None,
        "aramaMetni": None,
        "fonTurKod": None,
        "basSira": 1,
        "basTarih": today_str,
        "bitSira": 3000, # Sayfalama engelini aşmak için yüksek değer
        "bitTarih": today_str,
        "dil": "TR",
        "fonGrubu": None,
        "fonTurAciklama": None,
        "kurucuKodu": None,
        "sfonTurKod": None
    }
    
    try:
        print(f"Takasbank'tan {today_str} tarihli veriler çekiliyor...")
        r = requests.post(url, json=payload, headers=headers, impersonate="chrome110", timeout=60)
        
        if r.status_code != 200:
            print(f"Bağlantı Hatası! HTTP Kodu: {r.status_code}")
            exit(1)
            
        data = r.json()
        fund_list = data.get('resultList', [])
        
        if not fund_list:
            print("Veri boş döndü. Hafta sonu veya veri henüz girilmemiş olabilir.")
            exit(1)
            
        fund_map = {}
        for f in fund_list:
            code = f.get('fonKodu')
            # 'fiyat' veya 'sonFiyat' sütununu kontrol ediyoruz
            price = f.get('fiyat') or f.get('sonFiyat') or f.get('birimPayDegeri')
            
            if code and price is not None:
                try:
                    fund_map[code] = float(price)
                except (ValueError, TypeError):
                    pass
        
        # Sonuçları kaydet
        output = {
            "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "fonlar": fund_map
        }
        
        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"BAŞARILI! {len(fund_map)} adet fonun fiyatı güncellendi.")
        
    except Exception as e:
        print(f"Hata oluştu: {e}")
        exit(1)

if __name__ == "__main__":
    update_funds()
