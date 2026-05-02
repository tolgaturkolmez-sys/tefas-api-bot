import requests
import json
import sys
from datetime import date, timedelta

# Türkiye resmi tatilleri (MM-DD formatında, her yıl tekrar eder)
RECURRING_HOLIDAYS = {
    "01-01",  # Yılbaşı
    "04-23",  # Ulusal Egemenlik ve Çocuk Bayramı
    "05-01",  # Emek ve Dayanışma Günü
    "05-19",  # Atatürk'ü Anma, Gençlik ve Spor Bayramı
    "07-15",  # Demokrasi ve Millî Birlik Günü
    "08-30",  # Zafer Bayramı
    "10-29",  # Cumhuriyet Bayramı
}

def is_holiday(d):
    """Hafta sonu veya resmi tatil mi kontrol et."""
    if d.weekday() >= 5:
        return True
    if d.strftime("%m-%d") in RECURRING_HOLIDAYS:
        return True
    return False

def get_last_trading_day(d, max_lookback=10):
    """En son işlem gününü bul (tatil ve hafta sonu atla)."""
    for _ in range(max_lookback):
        if not is_holiday(d):
            return d
        d -= timedelta(days=1)
    return d

def fetch_tefas_data():
    trading_day = get_last_trading_day(date.today())
    date_str = trading_day.strftime("%d.%m.%Y")
    guncelleme_tarihi = trading_day.strftime("%Y-%m-%d")

    print(f"Bugün: {date.today()}, İşlem günü: {date_str}")

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

    session = requests.Session()
    try:
        session.get("https://www.tefas.gov.tr/", headers={"User-Agent": headers["User-Agent"]}, timeout=20)
    except Exception:
        pass

    # Doğru tarihi bulmak için geriye doğru dene (Ramazan/Kurban bayramı gibi dini tatiller için)
    records = []
    found_date = trading_day
    for attempt in range(10):
        attempt_date = trading_day - timedelta(days=attempt)
        if is_holiday(attempt_date):
            continue
        attempt_str = attempt_date.strftime("%d.%m.%Y")
        payload = {
            "fontip": "YAT",
            "bastarih": attempt_str,
            "bittarih": attempt_str,
            "fonkod": "",
        }
        try:
            resp = session.post(url, data=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            records = data.get("data", [])
            if records:
                found_date = attempt_date
                guncelleme_tarihi = found_date.strftime("%Y-%m-%d")
                print(f"Veri bulundu: {attempt_str} ({len(records)} fon)")
                break
            else:
                print(f"{attempt_str}: Veri yok (tatil/hafta sonu olabilir), önceki güne geçiliyor...")
        except Exception as e:
            print(f"{attempt_str}: İstek hatası - {e}")

    if not records:
        print("HATA: Son 10 iş günü için hiç veri alınamadı!")
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
        print("HATA: Yanıt alındı ama fon verisi parse edilemedi!")
        print("Örnek kayıt:", records[0] if records else "yok")
        sys.exit(1)

    output = {
        "guncellenme_tarihi": guncelleme_tarihi,
        "fonlar": all_funds,
    }

    file_path = "yatirim_fonlari .json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print(f"BAŞARILI! {len(all_funds)} fon '{file_path}' dosyasına yazıldı. Tarih: {guncelleme_tarihi}")

if __name__ == "__main__":
    fetch_tefas_data()
