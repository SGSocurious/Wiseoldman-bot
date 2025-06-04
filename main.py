import requests
import time
import json
import os

COMPETITION_ID = 92352
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
    url = f"https://api.wiseoldman.net/v2/competitions/{COMPETITION_ID}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Fout bij ophalen van competitiegegevens: {e}")
        return None

def build_update_message(changes, metric):
    lines = [f"📢 **Update voor competitie** *(metric: {metric})*\n"]
    for username, (old_gain, new_gain, delta) in changes.items():
        lines.append(f"🔹 **{username}**: +{delta} (was {old_gain} → nu {new_gain})")
    return "\n".join(lines)

def main_loop():
    print("🚀 Bot gestart...")
    while True:
        print("\n⏳ Ophalen van competitiegegevens...")

        data = fetch_competition_data()
        if not data:
            time.sleep(60)
            continue

        participants = data.get("participants", [])
        if not participants:
            print("⚠️ Geen deelnemers gevonden.")
            time.sleep(60)
            continue

        metric = data.get("metric", "onbekend_metric")
        print(f"📊 Metric: {metric}")
        print(f"👥 Aantal deelnemers: {len(participants)}")

        last_snapshot = load_snapshot()
        current_snapshot = {}
        changes = {}

        for p in participants:
            player_data = p.get("player", {})
            username = player_data.get("displayName")
            if not username:
                continue
            username_key = username.lower()

            progress = p.get("progress", {})
            gained = progress.get("gained")
            if gained is None:
                continue

            prev_gained = last_snapshot.get(username_key, 0)
            delta = gained - prev_gained

            print(f"🔍 {username}: vorige={prev_gained}, nu={gained}, verschil={delta}")

            current_snapshot[username_key] = gained

            if delta > 0:
                changes[username] = (prev_gained, gained, delta)

        if changes:
            msg = build_update_message(changes, metric)
            print(f"\n📤 Versturen naar Discord:\n{msg}")
            try:
                requests.post(WEBHOOK_URL, json={"content": msg})
            except Exception as e:
                print(f"❌ Fout bij verzenden naar Discord: {e}")
        else:
            print("ℹ️ Geen veranderingen, geen Discord update.")

        print(f"💾 Snapshot opslaan: {current_snapshot}")
        save_snapshot(current_snapshot)

        time.sleep(60)

if __name__ == "__main__":
    main_loop()
