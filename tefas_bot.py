import requests
import json
from datetime import datetime

# Ayarlar
url = "https://www.tefas.gov.tr/api/DB/BindFonAnalizList"
ana_sayfa = "https://www.tefas.gov.tr/FonAnaliz.aspx"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.tefas.gov.tr",
    "Referer": "https://www.tefas.gov.tr/FonAnaliz.aspx"
}

payload = {
    "fontipi": "YAT",
    "sfontipi": "",
    "bastarih": "",
    "bittarih": "",
    "islemgunu": ""
}

def verileri_guncelle():
    # 1. Oturum Başlat (Session kullanmak şart, çerezleri bu yönetir)
    session = requests.Session()
    
    try:
        # 2. Önce ana sayfaya git (Kapıdan giriş yapıp çerez alıyoruz)
        session.get(ana_sayfa, headers=headers, timeout=20)
        
        # 3. Veriyi iste
        response = session.post(url, data=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            veriler = response.json()
            if len(veriler) > 0:
                with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
                    json.dump(veriler, f, ensure_ascii=False, indent=4)
                print(f"Başarılı: {len(veriler)} adet fon kaydedildi.")
            else:
                print("Hata: TEFAS'tan veri geldi ama liste boş!")
                exit(1) # GitHub Actions'ın kırmızı yanmasını sağlar
        else:
            print(f"Hata: TEFAS {response.status_code} koduyla döndü.")
            exit(1)

    except Exception as e:
        print(f"Sistem Hatası: {str(e)}")
        exit(1)

if __name__ == "__main__":
    verileri_guncelle()
