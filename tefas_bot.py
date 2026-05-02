import requests
import json
import sys
import urllib3
from datetime import date, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

RECURRING_HOLIDAYS = {
    "01-01", "04-23", "05-01", "05-19",
    "07-15", "08-30", "10-29",
}

def is_holiday(d):
    if d.weekday() >= 5:
        return True
    if d.strftime("%m-%d") in RECURRING_HOLIDAYS:
        return True
    return False

def fetch_tefas_data():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.tefas.gov.tr",
    })

    # Önce TarihselVeriler sayfasına gidip cookie al
    referer = "https://www.tefas.gov.tr/TarihselVeriler.aspx"
    try:
        session.get(referer, verify=False, timeout=20)
        session.headers.update({"Referer": referer})
    except Exception:
        pass

    # BindHistoryInfo: tarih formatı YYYY-MM-DD
    url = "https://www.tefas.gov.tr/api/DB/BindHistoryInfo"

    today = date.today()
    records = []
    found_date = None

    for i in range(14):
        attempt = today - timedelta(days=i)
        if is_holiday(attempt):
            continue

        date_str = attempt.strftime("%Y-%m-%d")
        print(f"Deneniyor: {date_str}")

        payload = {
            "fontip": "YAT",
            "bastarih": date_str,
            "bittarih": date_str,
            "fonkod": "",
        }

        try:
            resp = session.post(url, data=payload, verify=False, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            records = data.get("data", [])
            if records:
                found_date = attempt
                print(f"Veri bulundu: {date_str} ({len(records)} fon)")
                break
            else:
                print(f"{date_str}: Veri yok")
        except Exception as e:
            print(f"{date_str}: Hata - {e}")

    if not records:
        print("HATA: Son 14 günde veri alınamadı!")
        sys.exit(1)

    all_funds = {}
    for row in records:
        if isinstance(row, dict):
            kod = str(row.get("FONKODU", "")).strip()
            raw = row.get("FIYAT", "0")
        elif isinstance(row, list) and len(row) >= 2:
            kod = str(row[0]).strip()
            raw = row[1]
        else:
            continue
        if not kod:
            continue
        try:
            fiyat = float(str(raw).replace(",", "."))
        except (ValueError, TypeError):
            fiyat = 0.0
        all_funds[kod] = round(fiyat, 6)

    if not all_funds:
        print("HATA: Veri parse edilemedi. Örnek kayıt:", records[0])
        sys.exit(1)

    output = {
        "guncellenme_tarihi": found_date.strftime("%Y-%m-%d"),
        "fonlar": all_funds,
    }

    file_path = "yatirim_fonlari .json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print(f"BAŞARILI! {len(all_funds)} fon yazıldı. Tarih: {found_date}")

if __name__ == "__main__":
    fetch_tefas_data()
