from tefas import Crawler
import json
import pandas as pd
import sys

def verileri_cek_ve_kaydet():
    try:
        # 1. Uzman kütüphaneyi çalıştırıyoruz
        crawler = Crawler()
        
        # 2. TEFAS'tan güncel fon verilerini çekiyoruz
        # (Bu kütüphane 10 Nisan'da gelen engelleri aşmak için güncellendi)
        df = crawler.fetch()
        
        if df is not None and not df.empty:
            # 3. Veriyi JSON formatına dönüştür
            veriler = df.to_dict(orient='records')
            
            with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
                json.dump(veriler, f, ensure_ascii=False, indent=4)
            
            print(f"BAŞARILI! {len(veriler)} adet fon kaydedildi.")
        else:
            print("HATA: TEFAS'tan veri çekilemedi (Liste boş döndü).")
            sys.exit(1) # GitHub Actions'ın kırmızı yanmasını sağlar

    except Exception as e:
        print(f"SİSTEM HATASI: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    verileri_cek_ve_kaydet()
