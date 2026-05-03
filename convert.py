import pandas as pd
import json
import os
import sys

def csv_to_json():
    csv_file = 'tefas.csv'
    json_file = 'yatirim_fonlari.json'

    if not os.path.exists(csv_file):
        print(f"Hata: {csv_file} bulunamadı.")
        sys.exit(1)

    try:
        # TEFAS CSV yapısına göre ilk 3 satırı atlayıp başlıkları alıyoruz
        df = pd.read_csv(csv_file, sep=',', encoding='utf-8-sig', skiprows=3)
        
        # Sütun isimlerini temizle
        df.columns = [c.strip() for c in df.columns]

        # Sayısal temizlik (Flutter'da hata almamak için)
        if 'Fiyat' in df.columns:
            df['Fiyat'] = df['Fiyat'].astype(str).str.replace('"', '').str.replace(',', '.')
            df['Fiyat'] = pd.to_numeric(df['Fiyat'], errors='coerce')

        data_list = df.to_dict(orient='records')
        
        output = {
            # Flutter'daki DateTime.parse() için ISO formatı (YYYY-MM-DD) en sağlıklısıdır
            "guncellenme_tarihi": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            "fon_sayisi": len(data_list),
            "fonlar": data_list  # Flutter kodunun beklediği anahtar ismi
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"Başarılı: JSON yapısı mobil uygulamaya uyarlandı ({len(data_list)} fon).")

    except Exception as e:
        print(f"Dönüştürme hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    csv_to_json()
