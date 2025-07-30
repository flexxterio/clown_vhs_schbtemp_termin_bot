import requests
from bs4 import BeautifulSoup
import asyncio
import os
import logging
from telegram import Bot
from telegram.constants import ParseMode
import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)

# Get environment variables for Telegram credentials
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Initialize Telegram bot
bot = Bot(token=TELEGRAM_TOKEN)

# URLs to check for appointments
URLS = {
    "Current month": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&select_month=0",
    "Next month": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&select_month=1",
    "Month after next": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&select_month=2"
}

# Always request Russian version
HEADERS = {
    "Accept-Language": "ru-RU,ru;q=0.9"
}

# Phrases indicating no appointments (in both Russian and English)
NO_APPOINTMENTS_TEXTS = [
    "пожалуйста, выберите дату, чтобы увидеть доступное время.",
    "please select a date to see available appointments."
]

def check_slots():
    """Checks each URL for available appointments.
    Returns a list of messages about available slots."""
    available = []
    for label, url in URLS.items():
        try:
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().lower()
            logging.info(f"[{datetime.datetime.now()}] Checked: {label}")
            # Check that none of the 'no appointments' phrases are present
            if not any(phrase in page_text for phrase in NO_APPOINTMENTS_TEXTS):
                logging.info(f"Available slot detected for: {label}")
                available.append(f"<b>{label}</b>: Possible free slot!\n{url}")
            else:
                logging.info(f"No slot found for: {label}")
        except Exception as e:
            logging.error(f"Error checking {label}: {e}")
    return available

async def main():
    """Main async loop: periodically checks for available appointments and sends notifications."""
    seen = set()
    while True:
        try:
            logging.info(f"Bot loop is alive at {datetime.datetime.now()}")
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
    asyncio.run(main())
)

