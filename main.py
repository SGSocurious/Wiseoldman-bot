import requests
import time
import json
import os

COMPETITION_ID = 90678
WEBHOOK_URL = "https://discord.com/api/webhooks/1379865773727547422/XB3C3tzt8pPV_8xf_pFsPlbz7_bfm1a0gb055tlY8QcZW5-jYK1MTtYYlRh35deYihcw"
SNAPSHOT_FILE = "last_snapshot.json"

def load_snapshot():
    if os.path.exists(SNAPSHOT_FILE):
        try:
            with open(SNAPSHOT_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Kon snapshot niet inladen, JSON is ongeldig.")
    return {}

def save_snapshot(snapshot):
    try:
        with open(SNAPSHOT_FILE, "w") as f:
            json.dump(snapshot, f)
    except Exception as e:
        print(f"❌ Fout bij opslaan van snapshot: {e}")

def fetch_competition_data():
    url = f"https://api.wiseoldman.net/v2/competitions/{COMPETITION_ID}?expand=participations"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Fout bij ophalen van competitiegegevens: {e}")
        return None

def main_loop():
    print("🚀 Bot gestart...")
    while True:
        print("\n⏳ Ophalen van competitiegegevens...")

        data = fetch_competition_data()
        if not data:
            time.sleep(30)
            continue

        # Print de hele data keys en of participations er in zitten
        print(f"DEBUG: Keys in response: {list(data.keys())}")
        participations = data.get("participations", None)
        if participations is None:
            print("⚠️ 'participations' is None! Controleer of '?expand=participations' werkt.")
            time.sleep(30)
            continue

        print(f"DEBUG: Aantal deelnemers: {len(participations)}")
        if len(participations) == 0:
            print("⚠️ Geen deelnemers gevonden.")
            time.sleep(30)
            continue

        # Print deelnemersnamen en hun gained waarde
        for p in participations:
            player_data = p.get("player", {})
            username = player_data.get("displayName", "<onbekend>")
            progress = p.get("progress", {})
            gained = progress.get("gained", "<geen gained>")
            print(f"DEBUG: Speler {username} heeft gained = {gained}")

        # Even stoppen hier om eerst te controleren wat binnenkomt
        print("🔧 Debugcheck klaar, script pauzeert 60 seconden.")
        time.sleep(60)

if __name__ == "__main__":
    main_loop()
