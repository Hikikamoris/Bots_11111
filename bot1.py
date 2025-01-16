import time
import feedparser
import asyncio
import json
from telegram import Bot
import re
import os

# Ваш токен бота и название канала
TOKEN = "8099129290:AAGptZmiE0jSbqami7mcO58AZHxoTUX-UZU"
CHANNEL_ID = "@vzglad_today"

# Список URL RSS-источников
RSS_FEED_URLS = [
    "https://russian.rt.com/rss",  # Пример 1
    "https://lenta.ru/rss/google-newsstand/main/",  # Пример 2
    "https://www.rbc.ru/rbcfreenews/index.rss",  # Пример 3
    # Добавьте сюда другие источники
]

# Путь к файлу для хранения опубликованных ссылок
PUBLISHED_LINKS_FILE = "published_links.json"

# Инициализация бота
bot = Bot(token=TOKEN)

# Функция для загрузки опубликованных ссылок из файла
def load_published_links():
    if os.path.exists(PUBLISHED_LINKS_FILE):
        with open(PUBLISHED_LINKS_FILE, "r") as file:
            return set(json.load(file))
    return set()

# Функция для сохранения опубликованных ссылок в файл
def save_published_links(links):
    with open(PUBLISHED_LINKS_FILE, "w") as file:
        json.dump(list(links), file)

# Загрузка опубликованных ссылок
published_links = load_published_links()

# Функция для очистки HTML-тегов, кроме поддерживаемых
def clean_html(text):
    # Заменить тег <br> на перенос строки
    text = re.sub(r'<br>', '\n', text)
    # Удалить все теги, которые не поддерживаются
    text = re.sub(r'<[^>]+>', '', text)
    return text

# Функция для удаления ненужных "Читать далее" в конце текста
def remove_read_more(text):
    # Удаляем все вхождения "Читать далее", которые не являются ссылками
    text = re.sub(r'Читать далее.*', '', text)
    return text

# Асинхронная функция для получения и отправки постов
async def fetch_and_post():
    global published_links
    for rss_feed_url in RSS_FEED_URLS:
        feed = feedparser.parse(rss_feed_url)

        for entry in feed.entries:
            # Проверка на уникальность поста
            if entry.link not in published_links:
                # Очистка текста от неподдерживаемых тегов
                clean_title = clean_html(entry.title)
                clean_summary = clean_html(entry.summary)

                # Удаление ненужных "Читать далее" в конце
                clean_summary = remove_read_more(clean_summary)

                # Форматирование текста с кликабельной ссылкой "Читать далее"
                message = f"<b>{clean_title}</b>\n\n{clean_summary}\n\n<a href='{entry.link}'>Читать далее</a>"

                # Если есть изображение, отправляем его
                if 'media_content' in entry:
                    for media in entry['media_content']:
                        if 'url' in media:
                            image_url = media['url']
                            # Публикация изображения
                            await bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=message, parse_mode="HTML")
                            break
                else:
                    # Если изображения нет, отправляем только текст
                    await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="HTML")

                # Добавление ссылки в список опубликованных
                published_links.add(entry.link)
                save_published_links(published_links)  # Сохраняем опубликованные ссылки

                # Задержка между публикациями (30 секунд)
                await asyncio.sleep(30)

# Запуск асинхронной функции
async def main():
    print("Бот запущен и работает!")
    while True:
        await fetch_and_post()
        # Интервал проверки новых записей (каждые 10 минут)
        await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(main())


