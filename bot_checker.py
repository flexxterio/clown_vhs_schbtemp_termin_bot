import requests
from bs4 import BeautifulSoup
import time
from telegram import Bot
import os
import threading
from keep_alive import keep_alive

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TELEGRAM_TOKEN)

URLS = {
    "Current month": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&separate_appointment_reason_first=1&select_month=0",
    "Next month": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&separate_appointment_reason_first=1&select_month=1",
    "Month after next": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&separate_appointment_reason_first=1&select_month=2"
}

def check_slots():
    found = []
    for name, url in URLS.items():
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        no_appts = soup.find("p", string=lambda s: s and "No appointments avaialable" in s)
        if not no_appts:
            found.append(f"{name}: possibly free slot!\n{url}")
    return found

def run_checker():
    seen = set()
    while True:
        try:
            results = check_slots()
            for msg in results:
                if msg not in seen:
                    bot.send_message(chat_id=CHAT_ID, text=msg)
                    seen.add(msg)
            time.sleep(300)
        except Exception as e:
            bot.send_message(chat_id=CHAT_ID, text=f"[Error] {e}")
            time.sleep(300)

if __name__ == "__main__":
    keep_alive()  # Start Flask server
    thread = threading.Thread(target=run_checker)
    thread.start()
