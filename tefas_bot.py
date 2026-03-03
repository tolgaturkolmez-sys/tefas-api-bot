import requests
import json
import pandas as pd
from datetime import datetime, timedelta

def get_tefas_data():
    url = "https://www.tefas.gov.tr/api/DB/BindHistoryInfo"
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)
    
    payload = {
        "fontip": "YAT",
        "sfontip": "",
        "bastarih": start_date.strftime("%d.%m.%Y"),
        "bittarih": end_date.strftime("%d.%m.%Y")
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.tefas.gov.tr/FonAnaliz.aspx",
        "Origin": "https://www.tefas.gov.tr"
    }
    
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            raw_data = response.json()
            if 'data' not in raw_data or not raw_data['data']:
                print("HATA: Veri bulunamadı.")
                return
                
            df = pd.DataFrame(raw_data['data'])
            
            # --- KRİTİK DÜZELTME BURASI ---
            # Eğer tarih sayısal gelirse milisaniyeden çevir, metin gelirse formatla oku
            if pd.to_numeric(df['TARIH'], errors='coerce').notnull().all():
                df['date_dt'] = pd.to_datetime(df['TARIH'].astype(float), unit='ms')
            else:
                df['date_dt'] = pd.to_datetime(df['TARIH'], format='%d.%m.%Y', errors='coerce')
            # ------------------------------

            latest_date = df['date_dt'].max()
            latest_df = df[df['date_dt'] == latest_date]
            
            result = {row['FONKODU']: row['FIYAT'] for _, row in latest_df.iterrows()}
            
            export_data = {
                "guncellenme_tarihi": latest_date.strftime("%Y-%m-%d"),
                "fonlar": result
            }
            
            with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
                
            print(f"BAŞARILI! {len(result)} fon kaydedildi. Tarih: {latest_date.strftime('%Y-%m-%d')}")
        else:
            print(f"API Hatası: {response.status_code}")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    get_tefas_data()
