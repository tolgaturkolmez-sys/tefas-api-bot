import requests
import json
import sys
from datetime import date, timedelta

def get_last_weekday(d):
    """Hafta sonu ise son iş gününe çek."""
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d

def fetch_tefas_data():
    today = get_last_weekday(date.today())
    date_str = today.strftime("%d.%m.%Y")
    guncelleme_tarihi = today.strftime("%Y-%m-%d")

    url = "https://www.tefas.gov.tr/api/DB/BindHistoryInfo"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.tefas.gov.tr",
        "Referer": "https://www.tefas.gov.tr/",
    }

    payload = {
        "fontip": "YAT",
        "bastarih": date_str,
        "bittarih": date_str,
        "fonkod": "",
    }

    print(f"TEFAS verisi çekiliyor ({date_str})...")

    session = requests.Session()
    # Önce ana sayfaya gidip cookie alalım
    try:
        session.get("https://www.tefas.gov.tr/", headers={"User-Agent": headers["User-Agent"]}, timeout=20)
    except Exception:
        pass

    try:
        resp = session.post(url, data=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"HATA: İstek başarısız - {e}")
        sys.exit(1)

    records = data.get("data", [])

    if not records:
        # Tatil günü olabilir, 3 gün geriye kadar dene
        print(f"Uyarı: {date_str} için veri yok. Önceki iş günleri deneniyor...")
        for i in range(1, 4):
            alt_date = get_last_weekday(today - timedelta(days=i))
            alt_str = alt_date.strftime("%d.%m.%Y")
            payload["bastarih"] = alt_str
            payload["bittarih"] = alt_str
            try:
                resp = session.post(url, data=payload, headers=headers, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                records = data.get("data", [])
                if records:
                    guncelleme_tarihi = alt_date.strftime("%Y-%m-%d")
                    print(f"Veri {alt_str} tarihi için bulundu.")
                    break
            except Exception:
                continue

    if not records:
        print("HATA: Hiçbir tarih için veri alınamadı!")
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
        print(f"HATA: Yanıt alındı ama fon verisi parse edilemedi!")
        print("Örnek kayıt:", records[0] if records else "yok")
        sys.exit(1)

    output = {
        "guncellenme_tarihi": guncelleme_tarihi,
        "fonlar": all_funds,
    }

    file_path = "yatirim_fonlari .json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print(f"BAŞARILI! {len(all_funds)} fon '{file_path}' dosyasına yazıldı.")

if __name__ == "__main__":
    fetch_tefas_data()
