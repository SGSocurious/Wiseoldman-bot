import requests
import time
import json
import os

COMPETITION_ID = 92352
WEBHOOK_URL = "https://discord.com/api/webhooks/1379865773727547422/XB3C3tzt8pPV_8xf_pFsPlbz7_bfm1a0gb055tlY8QcZW5-jYK1MTtYYlRh35deYihcw"
SLEEP_INTERVAL = 30
SNAPSHOT_FILE = "last_snapshot.json"

METRIC_LABELS = {
    "ehp": "EHP",
    "ehb": "EHB",
    "clue_all": "Clues",
    "boss_general_graardor": "KC",
    "hunter": "XP",
    "fishing": "XP",
    "magic": "XP",
    "runecraft": "XP",
}

def load_snapshot():
    if os.path.isfile(SNAPSHOT_FILE):
        with open(SNAPSHOT_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_snapshot(snapshot):
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snapshot, f)

def get_competition_data():
    url = f"https://api.wiseoldman.net/v2/competitions/{COMPETITION_ID}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()

    # Print volledige API response voor debugging (zorg dat het niet te groot is!)
    print("📡 Volledige API response:")
    print(json.dumps(data, indent=2))

    metric = data.get("metric", "unknown")
    participants = data.get("participants", [])
    print(f"📡 API returned metric: {metric}")
    print(f"👥 Aantal deelnemers: {len(participants)}")

    return metric, participants

def build_message(participants, last_snapshot, metric_label):
    lines = [f"📊 **Competition Update (last {SLEEP_INTERVAL}s, {metric_label})**"]
    current_snapshot = {}
    updates_found = False

    sorted_players = sorted(
        participants,
        key=lambda x: x.get("progress", {}).get("gained", 0),
        reverse=True
    )

    for idx, player in enumerate(sorted_players, start=1):
        username = player.get("player", {}).get("displayName", "Unknown")
        gained = player.get("progress", {}).get("gained", 0)
        gained = int(gained)  # Zorg dat het een int is
        prev_gained = int(last_snapshot.get(username, 0))
        diff = gained - prev_gained
        current_snapshot[username] = gained

        print(f"🔎 {username}: vorige {prev_gained}, huidig {gained}, verschil {diff}")

        if diff > 0:
            updates_found = True
            lines.append(f"**#{idx}** {username}: {gained:,} {metric_label} (+{diff:,})")

    return "\n".join(lines) if updates_found else None, current_snapshot

def send_to_discord(message):
    payload = {"content": message}
    try:
        r = requests.post(WEBHOOK_URL, json=payload)
        r.raise_for_status()
        print("✅ Update verzonden naar Discord.")
    except Exception as e:
        print(f"⚠️ Fout bij verzenden naar Discord: {e}")

def main_loop():
    last_snapshot = load_snapshot()

    while True:
        try:
            print("⏳ Ophalen van competitiegegevens...")
            metric, participants = get_competition_data()
            metric_label = METRIC_LABELS.get(metric, metric.upper())

            message, current_snapshot = build_message(participants, last_snapshot, metric_label)

            if message:
                send_to_discord(message)
            else:
                print("ℹ️ Geen veranderingen, geen Discord update.")

            print(f"💾 Snapshot opslaan: {current_snapshot}")
            save_snapshot(current_snapshot)
            last_snapshot = current_snapshot

        except Exception as e:
            print(f"❌ Fout: {e}")

        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main_loop()
