import requests
import time

# === INSTELLINGEN ===
COMPETITION_ID = 92352
WEBHOOK_URL = "https://discord.com/api/webhooks/1379865773727547422/XB3C3tzt8pPV_8xf_pFsPlbz7_bfm1a0gb055tlY8QcZW5-jYK1MTtYYlRh35deYihcw"
SLEEP_INTERVAL = 30  # elke 30 seconden

last_snapshot = {}
metric_label = "gain"  # default label (XP, KC, etc.)

# Optional: zet mapping van metrics → label
METRIC_LABELS = {
    "ehp": "EHP",
    "ehb": "EHB",
    "clue_all": "Clues",
    "boss_general_graardor": "KC",
    "hunter": "XP",
    "fishing": "XP",
    "magic": "XP",
    "runecraft": "XP",
    # Voeg meer toe als je wilt
}

def get_competition_data():
    global metric_label

    url = f"https://api.wiseoldman.net/v2/competitions/{COMPETITION_ID}"
    response = requests.get(url)
    response.raise_for_status()

    try:
        data = response.json()
    except ValueError:
        print("⚠️ API response is geen geldige JSON.")
        return None

    participants = data.get("participants", [])
    if not isinstance(participants, list):
        print("⚠️ 'participants' veld is geen lijst:", participants)
        return None

    # Haal metric op en zet label voor Discord output
    metric = data.get("metric", "unknown")
    metric_label = METRIC_LABELS.get(metric, metric.upper())

    return participants

def build_message(current_data):
    global last_snapshot
    lines = [f"📊 **Competition Update (last 30s, {metric_label})**"]
    current_snapshot = {}

    sorted_players = sorted(
        current_data,
        key=lambda x: x.get("progress", {}).get("gained", 0),
        reverse=True
    )

    updates_found = False

        for idx, player in enumerate(sorted_players[:10], start=1):
        player_info = player.get("player", {})
        username = player_info.get("displayName", "Unknown")
        gained = player.get("progress", {}).get("gained", 0)
        current_snapshot[username] = gained

        prev_gained = last_snapshot.get(username, 0)
        diff = gained - prev_gained

        print(f"🔎 {username}: vorige {prev_gained}, huidig {gained}, verschil {diff}")

        if diff > 0:
            updates_found = True
            lines.append(f"**#{idx}** {username}: {gained:,} {metric_label} (+{diff:,})")

    last_snapshot = current_snapshot

    if not updates_found:
        return None

    return "\n".join(lines)

def send_to_discord(message):
    payload = {"content": message}
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("✅ Update verzonden naar Discord.")
    except Exception as e:
        print(f"⚠️ Fout bij verzenden naar Discord: {e}")

def main_loop():
    while True:
        try:
            print("⏳ Ophalen van competitiegegevens...")
            data = get_competition_data()
            if data is None:
                raise Exception("Geen geldige data ontvangen van API.")

            message = build_message(data)
            if message:
                send_to_discord(message)
            else:
                print("ℹ️ Geen veranderingen, geen Discord update.")
        except Exception as e:
            print(f"❌ Fout: {e}")
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main_loop()
