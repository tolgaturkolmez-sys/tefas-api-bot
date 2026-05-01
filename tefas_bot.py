import requests
import pandas as pd
import json
from datetime import datetime

def fetch_tefas():
    url = "https://www.tefas.gov.tr/api/DB/BindHistoryInfo"

    payload = {
        "fontip": "YAT",
        "bastarih": datetime.now().strftime("%d.%m.%Y"),
        "bittarih": datetime.now().strftime("%d.%m.%Y")
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        print("❌ API HATA:", response.status_code)
        return None

    data = response.json()

    if "data" not in data:
        print("❌ API format değişmiş olabilir")
        return None

    df = pd.DataFrame(data["data"])

    print("📊 Satır sayısı:", len(df))
    print("📊 Kolonlar:", df.columns.tolist())

    return df


def json_uret(df):
    fonlar = {}

    for _, row in df.iterrows():
        kod = row.get("FONKODU") or row.get("FONKOD") or row.get("code")
        fiyat = row.get("FIYAT") or row.get("price") or row.get("PRICE")

        if kod and fiyat:
            fonlar[kod] = float(fiyat)

    if not fonlar:
        print("❌ Fon verisi boş, JSON oluşturulmadı")
        return

    cikti = {
        "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
        "fon_sayisi": len(fonlar),
        "fonlar": fonlar
    }

    with open("yatirim_fonlari.json", "w", encoding="utf-8") as f:
        json.dump(cikti, f, ensure_ascii=False, indent=2)

    print("✅ JSON oluşturuldu:", len(fonlar))


def main():
    df = fetch_tefas()

    if df is not None and not df.empty:
        json_uret(df)
    else:
        print("❌ Veri çekilemedi")


if __name__ == "__main__":
    main()
