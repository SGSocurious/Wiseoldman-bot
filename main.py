import requests
import time
import json
import os

COMPETITION_ID = 90678
WEBHOOK_URL = "https://discord.com/api/webhooks/1380961397214547989/tbp_zd_3JaszWvXi40d5XlmXNyjGrIFjHxJvz6rGSJWbZjXB5oL6dkvfxy7qG0kvhecZ"
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

def send_discord_update(message):
    data = {"content": message}
    try:
        resp = requests.post(WEBHOOK_URL, json=data)
        resp.raise_for_status()
        print("✅ Discord update verzonden.")
    except requests.RequestException as e:
        print(f"❌ Fout bij verzenden Discord update: {e}")

def main_loop():
    print("🚀 Bot gestart...")

    first_run = not os.path.exists(SNAPSHOT_FILE)
    last_snapshot = load_snapshot()

    while True:
        print("\n⏳ Ophalen van competitiegegevens...")
        data = fetch_competition_data()
        if not data:
            time.sleep(30)
            continue

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

        new_snapshot = {}
        changes = []

        for p in participations:
            player = p.get("player", {})
            username = player.get("displayName", "<onbekend>")
            progress = p.get("progress", {})
            gained = progress.get("gained", 0)

            player_id = str(p.get("playerId"))
            new_snapshot[player_id] = gained

            old_gained = last_snapshot.get(player_id, 0)
            diff = gained - old_gained

            print(f"DEBUG: Speler {username} heeft gained = {gained}, vorig = {old_gained}, verschil = {diff}")

            if not first_run and diff > 0:
                changes.append(f"🎉 {username} heeft {diff}x Vorkath gekilld!! (Totaal: {gained})")

        # Bij eerste run: alleen snapshot opslaan
        if first_run:
            print("📸 Eerste run: snapshot opgeslagen zonder Discord-update.")
            first_run = False
        elif changes:
            message = "**Update:**\n" + "\n".join(changes)
            send_discord_update(message)
        else:
            print("ℹ️ Geen veranderingen, geen Discord update.")

        save_snapshot(new_snapshot)
        last_snapshot = new_snapshot

        print("🔧 Debugcheck klaar, script pauzeert 60 seconden.")
        time.sleep(60)

if __name__ == "__main__":
    main_loop()
