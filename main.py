import requests
import time
import json
import os

COMPETITION_ID = 92352
WEBHOOK_URL = "https://discord.com/api/webhooks/1379865773727547422/XB3C3tzt8pPV_8xf_pFsPlbz7_bfm1a0gb055tlY8QcZW5-jYK1MTtYYlRh35deYihcw"
SNAPSHOT_FILE = "last_snapshot.json"


def load_snapshot():
    if os.path.exists(SNAPSHOT_FILE):
        with open(SNAPSHOT_FILE, "r") as f:
            return json.load(f)
    return {}


def save_snapshot(snapshot):
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snapshot, f)


def fetch_competition_data():
    url = f"https://api.wiseoldman.net/v2/competitions/{COMPETITION_ID}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ API fout: {response.status_code}")
        return None
    return response.json()


def build_update_message(changes, metric):
    lines = [f"📈 **Update voor competitie `{metric}`**\n"]
    for username, (old_gain, new_gain, delta) in changes.items():
        lines.append(f"🔹 **{username}**: +{delta} ({old_gain} → {new_gain})")
    return "\n".join(lines)


def main_loop():
    print("🚀 Bot gestart...")
    while True:
        print("\n⏳ Ophalen van competitiegegevens...")

        data = fetch_competition_data()
        if not data:
            print("⚠️ Geen data ontvangen van API.")
            time.sleep(30)
            continue

        participants = data.get("participants", [])
        metric = data.get("metric", "onbekend_metric")
        print(f"📊 Metric: {metric}")
        print(f"👥 Aantal deelnemers: {len(participants)}")

        last_snapshot = load_snapshot()
        current_snapshot = {}
        changes = {}

        for p in participants:
            player_data = p.get("player", {})
            username = player_data.get("displayName", "Onbekend")
            username_key = username.lower()

            progress = p.get("progress", {})
            gained = progress.get("gained", 0)

            prev_gained = last_snapshot.get(username_key, 0)
            delta = gained - prev_gained

            print(f"🔍 {username}: vorige={prev_gained}, nu={gained}, verschil={delta}")

            current_snapshot[username_key] = gained

            if delta > 0:
                changes[username] = (prev_gained, gained, delta)

        if changes:
            msg = build_update_message(changes, metric)
            print(f"\n📤 Versturen naar Discord:\n{msg}")
            requests.post(WEBHOOK_URL, json={"content": msg})
        else:
            print("ℹ️ Geen veranderingen, geen Discord update.")

        print(f"💾 Snapshot opslaan: {current_snapshot}")
        save_snapshot(current_snapshot)

        time.sleep(30)


if __name__ == "__main__":
    main_loop()
