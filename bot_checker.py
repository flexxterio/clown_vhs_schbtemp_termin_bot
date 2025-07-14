import requests
from bs4 import BeautifulSoup
import time
from telegram import Bot
import os

# Get bot token and chat ID from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Initialize the Telegram bot
bot = Bot(token=TELEGRAM_TOKEN)

# URLs for the current, next, and following month
URLS = {
    "Current month": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&separate_appointment_reason_first=1&select_month=0",
    "Next month": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&separate_appointment_reason_first=1&select_month=1",
    "Month after next": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&separate_appointment_reason_first=1&select_month=2"
}

def check_slots():
    """Check all configured pages for available appointment slots."""
    found = []
    for name, url in URLS.items():
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Look for the phrase that indicates no appointments
        no_appts = soup.find("p", string=lambda s: s and "No appointments avaialable" in s)
        # If the message is NOT found, assume there may be slots
        if not no_appts:
            found.append(f"{name}: possibly free slot!\n{url}")
    return found

def main():
    """Main loop that runs the bot every 5 minutes."""
    seen = set()
    while True:
        try:
            results = check_slots()
            for msg in results:
                if msg not in seen:
                    bot.send_message(chat_id=CHAT_ID, text=msg)
                    seen.add(msg)
            time.sleep(300)  # wait 5 minutes
        except Exception as e:
            bot.send_message(chat_id=CHAT_ID, text=f"[Error] {e}")
            time.sleep(300)

if __name__ == "__main__":
    main()
