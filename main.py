import requests
import time

# === INSTELLINGEN ===
COMPETITION_ID = 92352
WEBHOOK_URL = "https://discord.com/api/webhooks/1379865773727547422/XB3C3tzt8pPV_8xf_pFsPlbz7_bfm1a0gb055tlY8QcZW5-jYK1MTtYYlRh35deYihcw"
SLEEP_INTERVAL = 30  # in seconden (1 uur)

last_snapshot = {}

def get_competition_data():
    url = f"https://api.wiseoldman.net/v2/competitions/90678"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def build_message(current_data):
    global last_snapshot
    lines = ["📊 **Competition Update (last hour)**"]
    current_snapshot = {}

    # Controleer of we een lijst hebben
    if not isinstance(current_data, list):
        return "⚠️ API response unexpected: geen lijst ontvangen."

    # Sorteer deelnemers op XP-groei
    sorted_players = sorted(current_data, key=lambda x: x.get('progress', {}).get('gained', 0), reverse=True)

    for idx, player in enumerate(sorted_players[:10], start=1):
        player_data = player.get('player', {})
        username = player_data.get('displayName', 'Unknown')
        gained = player.get('progress', {}).get('gained', 0)
        rank_change = ""
        current_snapshot[username] = gained

        if username in last_snapshot:
            diff = gained - last_snapshot[username]
            if diff > 0:
                rank_change = f" (+{diff:,} xp)"
            elif diff == 0:
                rank_change = " (no gain)"
        else:
            rank_change = f" (+{gained:,} xp)"

        lines.append(f"**#{idx}** {username}: {gained:,} xp{rank_change}")

    last_snapshot = current_snapshot
    return "\n".join(lines)


def send_to_discord(message):
    payload = {
        "content": message
    }
    response = requests.post(WEBHOOK_URL, json=payload)
    response.raise_for_status()

def main_loop():
    while True:
        try:
            data = get_competition_data()
            print("DEBUG: API response:", data)
            message = build_message(data)
            send_to_discord(message)
            print("✅ Discord update verstuurd.")
        except Exception as e:
            print(f"⚠️ Fout: {e}")
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main_loop()
