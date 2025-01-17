import asyncio
import feedparser
import re
from telegram import Bot, ParseMode
from telegram.ext import Updater, CallbackContext
import time
import httpx

TOKEN = "8099129290:AAGptZmiE0jSbqami7mcO58AZHxoTUX-UZU"
CHANNEL_ID = "@vzglad_today"

RSS_FEED_URLS = [
    "https://russian.rt.com/rss",
    "https://www.rbc.ru/rbcfreenews/index.rss",
]

bot = Bot(token=TOKEN)

# Проверим, есть ли сообщения, которые были опубликованы в последние 12 часов
async def fetch_past_posts():
    current_time = time.time()
    cutoff_time = current_time - 12 * 3600  # 12 часов назад
    past_links = set()
    
    try:
        updates = await bot.get_chat(CHANNEL_ID).get_history(limit=100)
        for update in updates:
            if update.date.timestamp() > cutoff_time:  # Проверка по времени
                if update.entities:
                    for entity in update.entities:
                        if entity.type == "url":
                            link = update.text[entity.offset:entity.offset + entity.length]
                            past_links.add(link)
    except Exception as e:
        print(f"Ошибка получения истории сообщений: {e}")
    return past_links

# Получение и отправка новых постов
async def fetch_and_post():
    past_links = await fetch_past_posts()

    async with httpx.AsyncClient() as client:
        for rss_feed_url in RSS_FEED_URLS:
            try:
                response = await client.get(rss_feed_url)
                feed = feedparser.parse(response.text)
                for entry in feed.entries:
                    if entry.link not in past_links:
                        clean_title = clean_html(entry.title)
                        clean_summary = clean_html(entry.summary)
                        clean_summary = remove_read_more(clean_summary)

                        message = f"<b>{clean_title}</b>\n\n{clean_summary}\n\n<a href='{entry.link}'>Читать далее</a>"
                        await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=ParseMode.HTML)
                        await asyncio.sleep(30)  # Задержка между отправками
            except Exception as e:
                print(f"Ошибка при обработке фида {rss_feed_url}: {e}")

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
    asyncio.run(main())








