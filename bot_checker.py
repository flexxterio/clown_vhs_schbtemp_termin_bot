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
    "Current month": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&separate_appointment_reason_first=1&select_month=0",
    "Next month": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&separate_appointment_reason_first=1&select_month=1",
    "Month after next": "https://vhs-tempelhof-schoeneberg.appointmind.net/?&separate_appointment_reason_first=1&select_month=2"
}

def check_slots():
    found = []
    headers = {
        "Accept-Language": "ru-RU,ru;q=0.9"
    }
    for name, url in URLS.items():
        try:
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            text = soup.text.lower()
            if "no appointments avaialable" not in text:
                found.append(f"{name}: possiblz a termin\n{url}")
        except Exception as e:
            print(f"[ERROR] Exception while checking {name}: {e}")
    return found

async def main():
    seen = set()
    while True:
        try:
            results = check_slots()
            for msg in results:
                if msg not in seen:
                    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode=ParseMode.HTML)
                    seen.add(msg)
            await asyncio.sleep(15)
        except Exception as e:
            await bot.send_message(chat_id=CHAT_ID, text=f"[Error] {e}")
            await asyncio.sleep(300)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
