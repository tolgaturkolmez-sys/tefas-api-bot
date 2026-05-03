import firebase_admin
from firebase_admin import credentials, firestore
import json

cred = credentials.Certificate("service_account.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

with open("yatirim_fonlari.json", "r", encoding="utf-8") as f:
    data = json.load(f)

db.collection("tefas").document("fonlar").set(data)

print("🔥 Firebase upload OK")
