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
        # 1. encoding='utf-8-sig' hem Türkçe karakterleri düzeltir hem de baştaki ï»¿ işaretini siler.
        # 2. skiprows=[0] diyerek CSV'nin en başındaki gereksiz tarih satırını atlıyoruz.
        # 3. sep=',' TEFAS CSV'leri genelde virgül ile ayrılır.
        df = pd.read_csv(csv_file, sep=',', encoding='utf-8-sig', skiprows=[0])
        
        # Sütun isimlerindeki olası boşlukları temizleyelim
        df.columns = [c.strip() for c in df.columns]

        # Sayısal alanlardaki tırnakları ve virgülleri temizleyip float yapalım (Opsiyonel ama önerilir)
        cols_to_fix = ['Fiyat', 'Fon Toplam Değer']
        for col in cols_to_fix:
            if col in df.columns:
                # Örn: "35,21" -> 35.21
                df[col] = df[col].astype(str).str.replace('"', '').str.replace(',', '.')
                df[col] = pd.to_numeric(df[col], errors='coerce')

        data_list = df.to_dict(orient='records')
        
        output = {
            "guncellenme_tarihi": pd.Timestamp.now().strftime('%d.%m.%Y %H:%M'),
            "fon_sayisi": len(data_list),
            "veriler": data_list
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"Başarılı: {len(data_list)} fon düzgünce dönüştürüldü.")

    except Exception as e:
        print(f"Dönüştürme hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    csv_to_json()
