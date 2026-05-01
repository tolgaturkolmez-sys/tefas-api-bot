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

    for _, row in df.iterrows():
        kod = row["FONKODU"]
        fiyat = row["FIYAT"]

        fonlar[kod] = fiyat

    cikti = {
        "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
        "fonlar": fonlar
    }

    with open("yatirim_fonlari.json", "w", encoding="utf-8") as f:
        json.dump(cikti, f, ensure_ascii=False, indent=2)

    print("✅ JSON oluşturuldu!")


df = fetch_tefas()

if df is not None and not df.empty:
    json_uret(df)
else:
    print("❌ Veri yok, JSON oluşturulmadı")
