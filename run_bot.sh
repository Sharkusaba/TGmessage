#!/bin/bash

source /путь/к/venv/bin/activate

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "Ошибка: Файл .env не найден!"
    echo "Создайте файл .env с необходимыми переменными"
    exit 1
fi

# Проверка установленных зависимостей
python3 -c "import telegram, python-dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Установка зависимостей..."
    pip3 install python-telegram-bot python-dotenv
fi

# Запуск бота
echo "Запуск Telegram бота..."
python3 bot.py

# Если бот упал, перезапускаем через 10 секунд
echo "Бот остановлен. Перезапуск через 10 секунд..."
sleep 10
exec "$0"
