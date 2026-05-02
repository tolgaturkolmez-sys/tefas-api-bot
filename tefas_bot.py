import json
import sys
from datetime import date, timedelta
from tefas import Crawler

def fetch_tefas_data():
    print("TEFAS verisi çekiliyor...")

    crawler = Crawler()

    # Bugünün tarihi
    today = date.today()
    # Hafta sonu veya tatil ihtimaline karşı son 5 iş günü aralığı
    start_date = today - timedelta(days=5)

    try:
        # Tüm YAT (Yatırım Fonu) tipindeki fonları çek
        df = crawler.fetch(
            start=start_date.strftime("%Y-%m-%d"),
            end=today.strftime("%Y-%m-%d"),
            type="YAT",
            columns=["code", "price", "date"]
        )
    except Exception as e:
        print(f"HATA: Veri çekilemedi: {e}")
        sys.exit(1)

    if df is None or df.empty:
        print("HATA: API bağlandı ama fon verisi boş geldi!")
        sys.exit(1)

    print(f"Toplam {len(df)} satır verisi alındı.")

    # Her fon için en güncel fiyatı al (en son tarihe göre)
    df_sorted = df.sort_values("date", ascending=False)
    latest = df_sorted.drop_duplicates(subset=["code"], keep="first")

    # En güncel güncelleme tarihi
    guncelleme_tarihi = latest["date"].max()
    if hasattr(guncelleme_tarihi, "strftime"):
        guncelleme_tarihi = guncelleme_tarihi.strftime("%Y-%m-%d")
    else:
        guncelleme_tarihi = str(guncelleme_tarihi)

    # Mevcut JSON formatına uygun çıktı: {"guncellenme_tarihi": "...", "fonlar": {"AAK": 35.21, ...}}
    fonlar = {}
    for _, row in latest.iterrows():
        kod = str(row["code"]).strip()
        fiyat = float(row["price"]) if row["price"] is not None else 0.0
        fonlar[kod] = round(fiyat, 6)

    output = {
        "guncellenme_tarihi": guncelleme_tarihi,
        "fonlar": fonlar
    }

    file_path = "yatirim_fonlari .json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print(f"BAŞARILI! {len(fonlar)} adet fon verisi '{file_path}' dosyasına yazıldı.")
    print(f"Güncelleme tarihi: {guncelleme_tarihi}")

if __name__ == "__main__":
    fetch_tefas_data()
