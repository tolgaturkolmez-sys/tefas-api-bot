import pandas as pd
import json
import os
import sys

def csv_to_json():
    csv_file = 'tefas.csv'
    json_file = 'yatirim_fonlari.json'

    # Dosya kontrolü
    if not os.path.exists(csv_file):
        print(f"Hata: {csv_file} bulunamadı. Lütfen CSV dosyasını yükleyin.")
        sys.exit(1)

    try:
        # TEFAS CSV'leri genellikle ';' ayraçlı ve 'iso-8859-9' (Türkçe) kodlamalıdır.
        # Eğer hata alırsan encoding='utf-8' veya 'windows-1254' dene.
        df = pd.read_csv(csv_file, sep=';', encoding='iso-8859-9')
        
        # Veri setindeki boşlukları temizle
        df.columns = [c.strip() for c in df.columns]
        
        # DataFrame'i sözlük listesine çevir
        data_list = df.to_dict(orient='records')
        
        # Çıktı formatını hazırla
        output = {
            "guncellenme_tarihi": pd.Timestamp.now().strftime('%d.%m.%Y %H:%M'),
            "fon_sayisi": len(data_list),
            "veriler": data_list
        }

        # JSON olarak kaydet
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"Başarılı: {len(data_list)} adet fon verisi {json_file} dosyasına yazıldı.")

    except Exception as e:
        print(f"Dönüştürme sırasında bir hata oluştu: {e}")
        sys.exit(1)

if __name__ == "__main__":
    csv_to_json()
