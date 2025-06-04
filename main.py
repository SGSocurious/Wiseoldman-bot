import requests
import time

# === INSTELLINGEN ===
COMPETITION_ID = 92352
WEBHOOK_URL = "https://discord.com/api/webhooks/1379865773727547422/XB3C3tzt8pPV_8xf_pFsPlbz7_bfm1a0gb055tlY8QcZW5-jYK1MTtYYlRh35deYihcw"
SLEEP_INTERVAL = 30  # elke 30 seconden

last_snapshot = {}

def get_competition_data():
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

    return participants

def build_message(current_data):
    global last_snapshot
    lines = ["📊 **Competition Update (last 30s)**"]
    current_snapshot = {}

    sorted_players = sorted(
        current_data,
        key=lambda x: x.get("progress", {}).get("gained", 0),
        reverse=True
    )

    for idx, player in enumerate(sorted_players[:10], start=1):
        player_info = player.get("player", {})
        username = player_info.get("displayName", "Unknown")
        gained = player.get("progress", {}).get("gained", 0)
        rank_change = ""
        current_snapshot[username] = gained

        if username in last_snapshot:
            diff = gained - last_snapshot[username]
            if diff > 0:
                rank_change = f" (+{diff:,} xp)"
            elif diff == 0:
                continue  # geen verandering, dus overslaan
        else:
            rank_change = f" (+{gained:,} xp)"

        lines.append(f"**#{idx}** {username}: {gained:,} xp{rank_change}")

    last_snapshot = current_snapshot

    if len(lines) == 1:
        return None  # geen updates

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
                print("ℹ️ Geen XP-veranderingen, geen Discord update.")

        except Exception as e:
            print(f"❌ Fout: {e}")
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main_loop()
