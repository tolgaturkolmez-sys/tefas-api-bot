import requests
import json

def get_tefas_data():
    # 1. Yeni ve daha güncel endpoint
    url = "https://www.tefas.gov.tr/api/DB/BindFonAnalizList"
    
    # 2. Oturum Başlat (Çerezleri otomatik yönetir)
    oturum = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.tefas.gov.tr/FonAnaliz.aspx",
        "Origin": "https://www.tefas.gov.tr"
    }

    payload = {
        "fontipi": "YAT",
        "sfontipi": "",
        "bastarih": "", # Boş bırakmak en güncel veriyi getirir
        "bittarih": "",
        "islemgunu": ""
    }

    try:
        # KRİTİK ADIM: Önce ana sayfaya git ki 'Session Cookie' oluşsun
        oturum.get("https://www.tefas.gov.tr/FonAnaliz.aspx", headers=headers, timeout=20)
        
        # Şimdi aynı oturum ile veriyi POST et
        # Not: Bazı durumlarda data=payload yerine json=payload denemek gerekebilir
        response = oturum.post(url, data=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            veriler = response.json()
            print(f"Başarılı! {len(veriler)} adet fon bulundu.")
            return veriler
        else:
            print(f"Hata: TEFAS {response.status_code} koduyla yanıt verdi.")
            return None
            
    except Exception as e:
        print(f"Sistem Hatası: {e}")
        return None
