import time
import feedparser
import asyncio
import json
from telegram import Bot
import re
from datetime import datetime, timedelta

TOKEN = "8099129290:AAGptZmiE0jSbqami7mcO58AZHxoTUX-UZU"
CHANNEL_ID = "@vzglad_today"

RSS_FEED_URLS = [
    "https://russian.rt.com/rss", 
    "https://www.rbc.ru/rbcfreenews/index.rss",
]

bot = Bot(token=TOKEN)

# Словарь для хранения ссылок с временными метками
published_links = {}

# Время, после которого посты считаются старыми
TIME_LIMIT = timedelta(hours=12)

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
            # Проверяем, была ли уже опубликована ссылка в последние 12 часов
            link = entry.link
            if link in published_links:
                last_published_time = published_links[link]
                if datetime.now() - last_published_time < TIME_LIMIT:
                    continue  # Пропускаем, если ссылка была опубликована менее 12 часов назад

            clean_title = clean_html(entry.title)
            clean_summary = clean_html(entry.summary)
            clean_summary = remove_read_more(clean_summary)

            message = f"<b>{clean_title}</b>\n\n{clean_summary}\n\n<a href='{link}'>Читать далее</a>"

            if 'media_content' in entry:
                for media in entry['media_content']:
                    if 'url' in media:
                        image_url = media['url']
                        await bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=message, parse_mode="HTML")
                        break
            else:
                await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="HTML")

            # Обновляем временную метку публикации
            published_links[link] = datetime.now()

            await asyncio.sleep(30)

async def main():
    print("Бот запущен и работает!")
    while True:
        await fetch_and_post()
        await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(main())





