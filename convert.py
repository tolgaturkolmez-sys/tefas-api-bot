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
        # TEFAS CSV yapısında başlıklar 4. satırdadır (index 3)
        df = pd.read_csv(csv_file, sep=',', encoding='utf-8-sig', skiprows=3)
        
        # Sütun isimlerini temizle
        df.columns = [c.strip() for c in df.columns]

        # Fon Kodu ve Fiyat sütunlarının varlığını kontrol et
        if 'Fon Kodu' not in df.columns or 'Fiyat' not in df.columns:
            print("Hata: Gerekli sütunlar (Fon Kodu veya Fiyat) bulunamadı.")
            sys.exit(1)

        # Fiyatları sayısal formata (float) çevir
        # Örn: "35,215392" -> 35.215392
        def temizle_fiyat(val):
            try:
                return float(str(val).replace('"', '').replace(',', '.'))
            except:
                return 0.0

        # Yeni Key-Value yapısını oluştur
        fon_sozlugu = {}
        for _, row in df.iterrows():
            kod = str(row['Fon Kodu']).strip()
            fiyat = temizle_fiyat(row['Fiyat'])
            if kod:
                fon_sozlugu[kod] = fiyat

        # İstediğin final format
        output = {
            "guncellenme_tarihi": pd.Timestamp.now().strftime('%Y-%m-%d'),
            "fonlar": fon_sozlugu
        }

        # JSON olarak kaydet
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"Başarılı: {len(fon_sozlugu)} fon istediğin formatta kaydedildi.")

    except Exception as e:
        print(f"Dönüştürme hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    csv_to_json()
