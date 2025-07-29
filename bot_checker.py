import requests
from bs4 import BeautifulSoup
import asyncio
import os
import logging
from telegram import Bot
from telegram.constants import ParseMode
from keep_alive import keep_alive

# Setup logging
logging.basicConfig(level=logging.INFO)

# Environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

# URLs to check
URLS = {
    "Current month": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&select_month=0",
    "Next month": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&select_month=1",
    "Month after next": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&select_month=2"
}

# Always request Russian version
HEADERS = {
    "Accept-Language": "ru-RU,ru;q=0.9"
}

# Text indicating no appointments
NO_APPOINTMENTS_TEXT = "Пожалуйста, выберите дату, чтобы увидеть доступное время."  # preserve typo

def check_slots():
    available = []
    for label, url in URLS.items():
        try:
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().lower()
            logging.info(f"Checked: {label}")
            if NO_APPOINTMENTS_TEXT not in page_text:
                logging.info(f"Available slot detected for: {label}")
                available.append(f"<b>{label}</b>: Possible free slot!\n{url}")
            else:
                logging.info(f"No slot found for: {label}")
        except Exception as e:
            logging.error(f"Error checking {label}: {e}")
    return available

async def main():
    seen = set()
    while True:
        try:
            results = check_slots()
            for message in results:
                if message not in seen:
                    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.HTML)
                    seen.add(message)
            await asyncio.sleep(300)
        except Exception as e:
            logging.exception("Error in main loop")
            await bot.send_message(chat_id=CHAT_ID, text=f"[Error] {e}")
            await asyncio.sleep(300)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
