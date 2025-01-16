import asyncio
import feedparser
import re
from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode
from aiogram.utils import executor
import os
import time

TOKEN = "8099129290:AAGptZmiE0jSbqami7mcO58AZHxoTUX-UZU"
CHANNEL_ID = "@vzglad_today"

RSS_FEED_URLS = [
    "https://russian.rt.com/rss",
    "https://www.rbc.ru/rbcfreenews/index.rss",
]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Проверим, есть ли сообщения, которые были опубликованы в последние 12 часов
async def fetch_past_posts():
    current_time = time.time()
    cutoff_time = current_time - 12 * 3600  # 12 часов назад
    messages = await bot.get_chat_history(CHANNEL_ID, limit=100)

    past_links = set()
    for message in messages:
        if message.date.timestamp() > cutoff_time:  # Проверка по времени
            if message.entities and message.entities[0].type == 'url':
                link = message.text[message.entities[0].offset:message.entities[0].offset + message.entities[0].length]
                past_links.add(link)
    return past_links

# Получение и отправка новых постов
async def fetch_and_post():
    past_links = await fetch_past_posts()
    
    for rss_feed_url in RSS_FEED_URLS:
        feed = feedparser.parse(rss_feed_url)
        if feed.bozo:
            print(f"Ошибка при парсинге {rss_feed_url}")
            continue

        for entry in feed.entries:
            if entry.link not in past_links:
                clean_title = clean_html(entry.title)
                clean_summary = clean_html(entry.summary)
                clean_summary = remove_read_more(clean_summary)

                message = f"<b>{clean_title}</b>\n\n{clean_summary}\n\n<a href='{entry.link}'>Читать далее</a>"

                if 'media_content' in entry:
                    for media in entry['media_content']:
                        if 'url' in media:
                            image_url = media['url']
                            await bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=message, parse_mode=ParseMode.HTML)
                            break
                else:
                    await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=ParseMode.HTML)

                await asyncio.sleep(30)  # Задержка между отправками

# Очищаем HTML-теги
def clean_html(text):
    text = re.sub(r'<br>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text

# Убираем текст "Читать далее"
def remove_read_more(text):
    text = re.sub(r'Читать далее.*', '', text)
    return text

# Главная функция
async def main():
    print("Бот запущен и работает!")
    while True:
        await fetch_and_post()
        await asyncio.sleep(600)  # Пауза в 10 минут

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)







