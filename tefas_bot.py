import requests
import json
import sys
from datetime import date, timedelta

def fetch_tefas_data():
    session = requests.Session()

    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.tefas.gov.tr",
        "Referer": "https://www.tefas.gov.tr/tr/fon-verileri?fundType=YAT",
    })

    # Cookie almak için önce ana sayfaya git
    print("Ana sayfadan cookie alınıyor...")
    try:
        session.get("https://www.tefas.gov.tr/tr/fon-verileri?fundType=YAT", timeout=30)
    except Exception as e:
        print(f"Cookie alınamadı (devam ediliyor): {e}")

    today = date.today()
    date_str = today.strftime("%d.%m.%Y")

    # Hafta sonu kontrolü - son iş gününe git
    weekday = today.weekday()
    if weekday == 5:  # Cumartesi
        today = today - timedelta(days=1)
    elif weekday == 6:  # Pazar
        today = today - timedelta(days=2)
    date_str = today.strftime("%d.%m.%Y")

    url = "https://www.tefas.gov.tr/api/DB/Bind2Container/GetFundData"

    all_funds = {}
    start = 0
    page_size = 500
    max_pages = 10
    guncelleme_tarihi = today.strftime("%Y-%m-%d")

    print(f"Fon verileri çekiliyor ({date_str})...")

    for page in range(max_pages):
        payload = {
            "fundType": "YAT",
            "startDate": date_str,
            "endDate": date_str,
            "order[0][column]": "0",
            "order[0][dir]": "asc",
            "start": str(start),
            "length": str(page_size),
            "draw": str(page + 1),
        }

        try:
            resp = session.post(url, data=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"Sayfa {page+1} hatası: {e}")
            if page == 0:
                sys.exit(1)
            break

        records = data.get("data", [])
        total = data.get("recordsTotal", 0)

        if not records:
            print(f"Sayfa {page+1}: Veri yok, duruyoruz.")
            break

        for row in records:
            # API genellikle liste döner: [kod, fiyat, ...]
            # veya dict: {"FONKODU": "AAK", "BIRIMPAYFIYATI": "35.21", ...}
            if isinstance(row, list):
                kod = str(row[0]).strip()
                try:
                    fiyat = float(str(row[1]).replace(",", "."))
                except:
                    fiyat = 0.0
            elif isinstance(row, dict):
                kod = str(row.get("FONKODU", row.get("code", ""))).strip()
                raw = row.get("BIRIMPAYFIYATI", row.get("price", row.get("FIYAT", "0")))
                try:
                    fiyat = float(str(raw).replace(",", "."))
                except:
                    fiyat = 0.0
            else:
                continue

            if kod:
                all_funds[kod] = round(fiyat, 6)

        print(f"Sayfa {page+1}: {len(records)} fon alındı (toplam şimdiye kadar: {len(all_funds)}, genel toplam: {total})")

        start += page_size
        if start >= total or len(records) < page_size:
            break

    if not all_funds:
        print("HATA: Hiç fon verisi alınamadı!")
        sys.exit(1)

    output = {
        "guncellenme_tarihi": guncelleme_tarihi,
        "fonlar": all_funds,
    }

    file_path = "yatirim_fonlari .json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print(f"\nBAŞARILI! {len(all_funds)} fon '{file_path}' dosyasına yazıldı.")

if __name__ == "__main__":
    fetch_tefas_data()
