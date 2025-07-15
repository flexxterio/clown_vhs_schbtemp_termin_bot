import requests
from bs4 import BeautifulSoup
import asyncio
import os
from telegram import Bot
from telegram.constants import ParseMode
from keep_alive import keep_alive

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

URLS = {
    "Current month": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&select_month=0",
    "Next month": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&select_month=1",
    "Month after next": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&select_month=2"
}

HEADERS = {
    "Accept-Language": "ru-RU,ru;q=0.9"
}

def check_slots():
    available = []
    for label, url in URLS.items():
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text().lower()
        if "no appointments avaialable" not in page_text:
            available.append(f"<b>{label}</b>: Possible free slot!\n{url}")
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
            await bot.send_message(chat_id=CHAT_ID, text=f"[Error] {e}")
            await asyncio.sleep(300)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())

