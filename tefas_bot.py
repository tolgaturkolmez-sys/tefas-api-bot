import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import os

def get_tefas_data():
    url = "https://www.tefas.gov.tr/api/DB/BindHistoryInfo"
    
    # Tarih aralığını 1 haftaya çıkarıyoruz (Garanti olsun)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    payload = {
        "fontip": "YAT",
        "sfontip": "", # Bazı durumlarda bu boş veri gerekebiliyor
        "bastarih": start_date.strftime("%d.%m.%Y"),
        "bittarih": end_date.strftime("%d.%m.%Y")
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.tefas.gov.tr",
        "Referer": "https://www.tefas.gov.tr/FonAnaliz.aspx"
    }
    
    print(f"TEFAS'tan veri isteniyor: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
    
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=20)
        print(f"API Yanıt Kodu: {response.status_code}")
        
        if response.status_code == 200:
            raw_data = response.json()
            if 'data' not in raw_data or not raw_data['data']:
                print("HATA: TEFAS boş veri döndürdü.")
                return
                
            df = pd.DataFrame(raw_data['data'])
            print(f"Toplam {len(df)} satır veri alındı.")

            df['date_dt'] = pd.to_datetime(df['TARIH'], format='%d.%m.%Y')
            latest_date = df['date_dt'].max()
            latest_df = df[df['date_dt'] == latest_date]
            
            result = {row['FONKODU']: row['FIYAT'] for _, row in latest_df.iterrows()}
            
            export_data = {
                "guncellenme_tarihi": latest_date.strftime("%Y-%m-%d"),
                "fonlar": result
            }
            
            with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
                
            print(f"BAŞARILI! {len(result)} fon kaydedildi. Dosya: yatirim_fonlari.json")
        else:
            print(f"HATA: API bağlantı sorunu. Kod: {response.status_code}")
    except Exception as e:
        print(f"KRİTİK HATA: {e}")

if __name__ == "__main__":
    get_tefas_data()
