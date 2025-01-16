import time
import feedparser
import asyncio
import redis
from telegram import Bot
import re

TOKEN = "8099129290:AAGptZmiE0jSbqami7mcO58AZHxoTUX-UZU"
CHANNEL_ID = "@vzglad_today"

RSS_FEED_URLS = [
    "https://russian.rt.com/rss", 
    "https://www.rbc.ru/rbcfreenews/index.rss",
]

REDIS_HOST = "localhost"  # Или используйте адрес хоста в облаке
REDIS_PORT = 6379
REDIS_DB = 0

bot = Bot(token=TOKEN)

# Подключение к Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def load_published_links():
    # Получаем список ссылок из Redis (если они есть)
    return set(redis_client.smembers("published_links"))

def save_published_links(links):
    # Сохраняем ссылки в Redis
    redis_client.sadd("published_links", *links)

def clean_html(text):
    text = re.sub(r'<br>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text

def remove_read_more(text):
    text = re.sub(r'Читать далее.*', '', text)
    return text

async def fetch_and_post():
    published_links = load_published_links()  # Получаем текущие опубликованные ссылки
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

                save_published_links([entry.link])  # Сохраняем новую ссылку в Redis
                await asyncio.sleep(30)

async def main():
    print("Бот запущен и работает!")
    while True:
        await fetch_and_post()
        await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(main())




