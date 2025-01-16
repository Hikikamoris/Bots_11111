import time
import feedparser
import asyncio
import json
from telegram import Bot
import re
import os

TOKEN = "8099129290:AAGptZmiE0jSbqami7mcO58AZHxoTUX-UZU"
CHANNEL_ID = "@vzglad_today"

RSS_FEED_URLS = [
    "https://russian.rt.com/rss", 
    "https://www.rbc.ru/rbcfreenews/index.rss",
]

PUBLISHED_LINKS_FILE = "published_links.json"

bot = Bot(token=TOKEN)

def load_published_links():
    if os.path.exists(PUBLISHED_LINKS_FILE):
        try:
            with open(PUBLISHED_LINKS_FILE, "r") as file:
                return set(json.load(file))
        except json.JSONDecodeError:
            return set()
    return set()

def save_published_links(links):
    with open(PUBLISHED_LINKS_FILE, "w") as file:
        json.dump(list(links), file)

published_links = load_published_links()

def clean_html(text):
    text = re.sub(r'<br>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text

def remove_read_more(text):
    text = re.sub(r'Читать далее.*', '', text)
    return text

async def fetch_and_post():
    global published_links
    for rss_feed_url in RSS_FEED_URLS:
        feed = feedparser.parse(rss_feed_url)
        if feed.bozo:
            print(f"Ошибка при парсинге {rss_feed_url}")
            continue

        for entry in feed.entries:
            if entry.link not in published_links:
                clean_title = clean_html(entry.title)
                clean_summary = clean_html(entry.summary)
                clean_summary = remove_read_more(clean_summary)

                message = f"<b>{clean_title}</b>\n\n{clean_summary}\n\n<a href='{entry.link}'>Читать далее</a>"

                if 'media_content' in entry:
                    for media in entry['media_content']:
                        if 'url' in media:
                            image_url = media['url']
                            await bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=message, parse_mode="HTML")
                            break
                else:
                    await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="HTML")

                published_links.add(entry.link)
                save_published_links(published_links)

                await asyncio.sleep(30)

async def main():
    print("Бот запущен и работает!")
    while True:
        await fetch_and_post()
        await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(main())



