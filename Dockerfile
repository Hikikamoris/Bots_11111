# Используем официальный образ Python 3.10
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код в контейнер
COPY . /app/

# Открываем порт для общения с ботом (если нужно)
EXPOSE 8000

# Указываем команду для запуска бота
CMD ["python", "bot1.py"]
