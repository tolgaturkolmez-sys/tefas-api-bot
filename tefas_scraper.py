from playwright.sync_api import sync_playwright
import json
from datetime import datetime

def scrape_tefas():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("🌐 TEFAS açılıyor...")
        page.goto("https://www.tefas.gov.tr/FonKarsilastirma.aspx")

        page.wait_for_timeout(5000)

        # Sayfadaki tabloyu çekiyoruz
        rows = page.query_selector_all("table tbody tr")

        fonlar = {}

        for row in rows:
            cols = row.query_selector_all("td")

            if len(cols) < 3:
                continue

            try:
                kod = cols[0].inner_text().strip()
                fiyat = cols[2].inner_text().strip().replace(",", ".")

                fonlar[kod] = float(fiyat)

            except:
                continue

        browser.close()

        return fonlar


def save_json(fonlar):
    data = {
        "guncellenme_tarihi": datetime.now().strftime("%Y-%m-%d"),
        "fon_sayisi": len(fonlar),
        "fonlar": fonlar
    }

    with open("yatirim_fonlari.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ JSON oluşturuldu:", len(fonlar))


def main():
    fonlar = scrape_tefas()

    if fonlar:
        save_json(fonlar)
    else:
        print("❌ Veri çekilemedi")


if __name__ == "__main__":
    main()
