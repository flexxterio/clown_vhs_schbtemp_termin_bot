import requests
from bs4 import BeautifulSoup
import threading
import os
import logging
from flask import Flask
from telegram import Bot
from telegram.constants import ParseMode
import time
import datetime

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TELEGRAM_TOKEN)

URLS = {
    "Current month": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&select_month=0",
    "Next month": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&select_month=1",
    "Month after next": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&select_month=2"
}

HEADERS = {"Accept-Language": "ru-RU,ru;q=0.9"}

NO_APPOINTMENTS_TEXTS = [
    "пожалуйста, выберите дату, чтобы увидеть доступное время.",
    "please select a date to see available appointments."
]

def check_slots():
    available = []
    for label, url in URLS.items():
        try:
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().lower()
            logging.info(f"[{datetime.datetime.now()}] Checked: {label}")
            if not any(phrase in page_text for phrase in NO_APPOINTMENTS_TEXTS):
                logging.info(f"Available slot detected for: {label}")
                available.append(f"<b>{label}</b>: Possible free slot!\n{url}")
            else:
                logging.info(f"No slot found for: {label}")
        except Exception as e:
            logging.error(f"Error checking {label}: {e}")
    return available

def background_loop():
    seen = set()
    while True:
        try:
            logging.info(f"Bot loop is alive at {datetime.datetime.now()}")
            results = check_slots()
            for message in results:
                if message not in seen:
                    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.HTML)
                    seen.add(message)
            time.sleep(300)
        except Exception as e:
            logging.exception("Error in main loop")
            try:
                bot.send_message(chat_id=CHAT_ID, text=f"[Error] {e}")
            except Exception as inner_e:
                logging.error(f"Failed to send error to telegram: {inner_e}")
            time.sleep(120)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == "__main__":
    thread = threading.Thread(target=background_loop)
    thread.daemon = True
    thread.start()
    app.run(host='0.0.0.0', port=8080)

