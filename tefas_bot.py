import json
from datetime import datetime, timedelta
from tefas import Crawler

def get_tefas_data():
    crawler = Crawler()
    # Hafta sonu boş dönmemesi için son 4 günün verisini tarıyoruz
    start_date = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # TEFAS'tan verileri çek
        data = crawler.fetch(start=start_date, end=end_date, columns=['code', 'date', 'price'])
        if data.empty:
            print("Veri bulunamadı.")
            return
            
        # En güncel tarihi bul
        latest_date = data['date'].max()
        latest_data = data[data['date'] == latest_date]
        
        # JSON formatına çevir
        result = {}
        for index, row in latest_data.iterrows():
            result[row['code']] = row['price']
        
        # Dosyaya kaydet
        export_data = {
            "guncellenme_tarihi": latest_date.strftime("%Y-%m-%d"),
            "fonlar": result
        }
        
        with open('yatirim_fonlari.json', 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
            
        print(f"Başarılı! Veriler güncellendi: {latest_date.strftime('%Y-%m-%d')}")
            
    except Exception as e:
        print(f"Kritik Hata: {e}")

if __name__ == "__main__":
    get_tefas_data()
