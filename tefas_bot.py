import requests
import json
import os
import sys

def fetch_tefas_data():
    # TEFAS'ın veri sağladığı asıl endpoint
    url = "https://www.tefas.gov.tr/api/DB/Bind2Container/GetFundData"
    
    # Tarayıcıyı birebir taklit etmek için gerekli başlıklar
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "www.tefas.gov.tr",
        "Origin": "https://www.tefas.gov.tr",
        "Referer": "https://www.tefas.gov.tr/tr/fon-verileri?fundType=YAT",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    # API'nin beklediği form datası
    # length: 3000 diyerek tüm fonları tek seferde çekiyoruz
    payload = {
        "fundType": "YAT",
        "order[0][column]": "0",
        "order[0][dir]": "asc",
        "start": "0",
        "length": "3000",
        "draw": "1"
    }

    print("TEFAS API isteği gönderiliyor...")
    
    try:
        # Session kullanarak cookie yönetimini simüle ediyoruz
        session = requests.Session()
        # Önce ana sayfaya bir GET atıp çerezleri alalım (opsiyonel ama güvenli)
        session.get("https://www.tefas.gov.tr/tr/fon-verileri?fundType=YAT", headers={"User-Agent": headers["User-Agent"]})
        
        # Asıl veri isteği
        response = session.post(url, data=payload, headers=headers, timeout=30)
        
        # Hata kontrolü
        if response.status_code != 200:
            print(f"HATA: Sunucu {response.status_code} koduyla yanıt verdi.")
            print("Yanıt içeriği:", response.text[:200])
            sys.exit(1)

        data = response.json()
        funds = data.get("data", [])

        if not funds:
            print("HATA: API bağlandı ama fon listesi boş geldi!")
            sys.exit(1)

        # JSON olarak kaydet
        file_path = 'yatirim_fonlari.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(funds, f, ensure_ascii=False, indent=4)
        
        print(f"BAŞARILI! {len(funds)} adet fon verisi '{file_path}' dosyasına yazıldı.")

    except Exception as e:
        print(f"BEKLENMEDİK HATA: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_tefas_data()
