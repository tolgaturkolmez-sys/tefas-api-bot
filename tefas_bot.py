import requests
import json

def veri_cek():
    # TEFAS'ın şu an kullandığı en güncel ve en az korumalı uç nokta
    url = "https://www.tefas.gov.tr/api/DB/BindFonAnalizList"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.tefas.gov.tr/FonAnaliz.aspx",
        "Accept": "application/json"
    }

    # 10 Nisan sonrası en stabil çalışan veri paketi
    payload = {
        "fontipi": "YAT",
        "sfontipi": "",
        "bastarih": "",
        "bittarih": "",
        "islemgunu": ""
    }

    print("Veri çekme işlemi başlatılıyor...")
    try:
        # Session kullanarak 'insan gibi' davranıyoruz
        with requests.Session() as s:
            s.get("https://www.tefas.gov.tr/FonAnaliz.aspx", headers=headers, timeout=10)
            r = s.post(url, data=payload, headers=headers, timeout=20)
            
            if r.status_code == 200:
                data = r.json()
                with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"BAŞARILI! {len(data)} adet fon dosyaya yazıldı.")
            else:
                print(f"HATA: TEFAS kapıyı açmadı. Durum Kodu: {r.status_code}")
                
    except Exception as e:
        print(f"SİSTEM HATASI: {e}")

if __name__ == "__main__":
    veri_cek()
