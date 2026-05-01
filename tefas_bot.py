import requests
import pandas as pd

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
