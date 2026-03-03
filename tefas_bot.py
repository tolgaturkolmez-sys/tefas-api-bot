import requests
import json
import pandas as pd
from datetime import datetime, timedelta

def get_tefas_data():
    url = "https://www.tefas.gov.tr/api/DB/BindHistoryInfo"
    
    # Son 3 günün verisini çek (Hafta sonu boşluğunu kapatmak için)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)
    
    payload = {
        "fontip": "YAT", # Yatırım fonları
        "bastarih": start_date.strftime("%d.%m.%Y"),
        "bittarih": end_date.strftime("%d.%m.%Y")
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            raw_data = response.json()
            if 'data' not in raw_data:
                print("Veri formatı hatalı.")
                return
                
            df = pd.DataFrame(raw_data['data'])
            if df.empty:
                print("Güncel veri bulunamadı.")
                return

            # En güncel tarihi bul ve veriyi filtrele
            df['date_dt'] = pd.to_datetime(df['TARIH'], format='%d.%m.%Y')
            latest_date = df['date_dt'].max()
            latest_df = df[df['date_dt'] == latest_date]
            
            # JSON formatına çevir (FONKODU: FIYAT)
            result = {}
            for _, row in latest_df.iterrows():
                result[row['FONKODU']] = row['FIYAT']
            
            export_data = {
                "guncellenme_tarihi": latest_date.strftime("%Y-%m-%d"),
                "fonlar": result
            }
            
            with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
                
            print(f"Başarılı! {len(result)} fon güncellendi. Tarih: {latest_date.strftime('%Y-%m-%d')}")
        else:
            print(f"TEFAS API Hatası: {response.status_code}")
    except Exception as e:
        print(f"Kritik Hata: {e}")

if __name__ == "__main__":
    get_tefas_data()
