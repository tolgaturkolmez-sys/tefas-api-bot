from tefas import Crawler
import pandas as pd
import json
from datetime import datetime, timedelta

def update_funds():
    print("🚀 TEFAS Bot başlatılıyor (Resmi PyPI Kütüphanesi Modu)...")
    
    try:
        crawler = Crawler()
        bugun = datetime.now()
        
        # Hafta sonu veya tatil riskine karşı son 5 günü tarıyoruz
        bes_gun_once = bugun - timedelta(days=5)
        
        baslangic = bes_gun_once.strftime("%Y-%m-%d")
        bitis = bugun.strftime("%Y-%m-%d")
        
        print(f"📡 Takasbank API'sine bağlanılıyor... ({baslangic} ile {bitis} arası tarama)")
        
        # Sadece Yatırım Fonlarını (YAT) çek
        df = crawler.fetch(start=baslangic, end=bitis, name="YAT", columns=['date', 'code', 'price'])
        
        if df is None or df.empty:
            print("❌ Veri bulunamadı. TEFAS API yanıt vermiyor olabilir.")
            exit(1)
            
        print(f"📊 Toplam {len(df)} ham veri satırı çekildi. Filtreleme başlıyor...")
        
        # Verileri en yeni tarihe göre sırala
        df = df.sort_values(by='date', ascending=False)
        
        # Aynı koda sahip fonların sadece EN GÜNCEL tarihli olanını tut, eskileri sil
        df_guncel = df.drop_duplicates(subset=['code'], keep='first')
        
        fund_map = {}
        for index, row in df_guncel.iterrows():
            code = row['code']
            price = row['price']
            
            if pd.notna(code) and pd.notna(price):
                try:
                    fund_map[str(code).strip()] = float(price)
                except (ValueError, TypeError):
                    pass
                    
        if not fund_map:
            print("❌ İşlenebilir fon listesi oluşturulamadı.")
            exit(1)
            
        # Mobil uygulama için JSON yapısı
        output = {
            "guncellenme_tarihi": bugun.strftime("%Y-%m-%d"),
            "fonlar": fund_map
        }
        
        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"🎉 MUHTEŞEM! Tarayıcılarla uğraşmadan {len(fund_map)} adet fon API'den başarıyla çekildi.")

    except Exception as e:
        print(f"❌ Kritik Hata: {e}")
        exit(1)

if __name__ == "__main__":
    update_funds()
