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
        # 1. TEFAS CSV'lerinde başlıklar genellikle 4. satırdadır (skiprows=3).
        # 2. utf-8-sig kullanarak Türkçe karakter ve BOM sorununu çözüyoruz.
        df = pd.read_csv(csv_file, sep=',', encoding='utf-8-sig', skiprows=3)
        
        # Sütun isimlerini temizle (boşlukları at)
        df.columns = [c.strip() for c in df.columns]

        # Sayısal alanları temizleme fonksiyonu (Örn: "35,21" -> 35.21)
        def clean_numeric(val):
            if pd.isna(val): return 0
            val = str(val).replace('"', '').replace('.', '').replace(',', '.')
            try:
                return float(val)
            except:
                return 0

        # Sayısal sütunları dönüştür
        if 'Fiyat' in df.columns:
            # Fiyatlarda binlik ayırıcı nokta olmayabilir, direkt temizliyoruz.
            df['Fiyat'] = df['Fiyat'].astype(str).str.replace('"', '').str.replace(',', '.')
            df['Fiyat'] = pd.to_numeric(df['Fiyat'], errors='coerce')

        if 'Fon Toplam Değer' in df.columns:
            df['Fon Toplam Değer'] = df['Fon Toplam Değer'].apply(clean_numeric)

        data_list = df.to_dict(orient='records')
        
        output = {
            "guncellenme_tarihi": pd.Timestamp.now().strftime('%d.%m.%Y %H:%M'),
            "fon_sayisi": len(data_list),
            "veriler": data_list
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"Başarılı: {len(data_list)} fon verisi temiz bir şekilde dönüştürüldü.")

    except Exception as e:
        print(f"Dönüştürme hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    csv_to_json()
