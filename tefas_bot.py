import requests
import pandas as pd
import json
from datetime import datetime

def fetch_tefas():
    url = "https://www.tefas.gov.tr/api/DB/BindHistoryInfo"

    payload = {
        "fontip": "YAT",
        "bastarih": "01.04.2026",
        "bittarih": "01.05.2026"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        print("Hata:", response.status_code)
        return None

    data = response.json()
    df = pd.DataFrame(data["data"])

    return df


def json_uret(df):
    fonlar = {}

    print("Kolonlar:", df.columns)

    for _, row in df.iterrows():
        kod = row.get("FONKODU") or row.get("FONKOD") or row.get("code")
        fiyat = row.get("FIYAT") or row.get("price") or row.get("PRICE")

        if kod and fiyat:
            fonlar[kod] = fiyat

    if not fonlar:
        print("❌ Fon verisi boş!")
        return

    cikti = {
        "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
        "fonlar": fonlar
    }

    with open("yatirim_fonlari.json", "w", encoding="utf-8") as f:
        json.dump(cikti, f, ensure_ascii=False, indent=2)

    print("✅ JSON oluşturuldu!", len(fonlar), "adet fon")
