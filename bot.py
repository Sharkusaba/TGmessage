import os
import random
import logging
import asyncio
from datetime import datetime, time
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем данные из .env
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))  # Чат для отправки фраз
ALERTS_CHAT_ID = int(os.getenv('ALERTS_CHAT_ID'))  # Чат для оповещений
INFO_CHAT_ID = int(os.getenv('INFO_CHAT_ID'))  # Чат для информации
ALERTS_THREAD_ID = int(os.getenv('ALERTS_THREAD_ID', 376))
INFO_THREAD_ID = int(os.getenv('INFO_THREAD_ID', 377))

# Хранилище для секретных фраз
secret_phrases = {
    'phrase1': None,
    'phrase2': None
}

# Списки слов для генерации фраз
words_list = [
    # Существительные
    'солнце', 'луна', 'звезда', 'ветер', 'дождь', 'снег', 'огонь', 'вода', 'земля',
    'воздух', 'лес', 'гора', 'река', 'море', 'океан', 'город', 'деревня', 'дорога',
    'дом', 'книга', 'перо', 'меч', 'щит', 'ключ', 'замок', 'окно', 'дверь', 'стена',
    
    # Прилагательные
    'быстрый', 'тихий', 'громкий', 'яркий', 'темный', 'светлый', 'теплый', 'холодный',
    'новый', 'старый', 'древний', 'современный', 'секретный', 'важный', 'особый',
    'красный', 'синий', 'зеленый', 'желтый', 'черный', 'белый', 'золотой', 'серебряный',
    
    # Глаголы (в инфинитиве или форме)
    'бежать', 'лететь', 'плыть', 'стоять', 'сидеть', 'лежать', 'смотреть', 'видеть',
    'слышать', 'говорить', 'молчать', 'ждать', 'искать', 'найти', 'потерять', 'дать',
    'взять', 'открыть', 'закрыть', 'начать', 'закончить', 'понять', 'знать', 'верить'
]

def generate_secret_phrase():
    """Генерирует секретную фразу из 3 случайных слов"""
    selected_words = random.sample(words_list, 3)
    return ' '.join(selected_words)

async def send_daily_phrases(context: ContextTypes.DEFAULT_TYPE):
    """Отправляет ежедневные секретные фразы в админский чат"""
    try:
        # Генерируем новые фразы
        secret_phrases['phrase1'] = generate_secret_phrase()
        secret_phrases['phrase2'] = generate_secret_phrase()
        
        # Формируем сообщение
        message_text = (
            "🎯 *Секретные фразы на сегодня*\n\n"
            f"🔑 *Фраза 1:* `{secret_phrases['phrase1']}`\n"
            f"📍 Направление: Оповещения и новости\n\n"
            f"🔑 *Фраза 2:* `{secret_phrases['phrase2']}`\n"
            f"📍 Направление: Информация\n\n"
            "💡 *Как использовать:*\n"
            "Отправьте сообщение, начинающееся с секретной фразы, и бот перешлет его в соответствующий чат."
        )
        
        # Отправляем в админский чат
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message_text,
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"Отправлены ежедневные фразы: {secret_phrases}")
        
    except Exception as e:
        logger.error(f"Ошибка при отправке ежедневных фраз: {e}")

async def handle_message(update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик входящих сообщений"""
    try:
        message = update.message
        if not message or not message.text:
            return
        
        user_text = message.text.strip()
        
        # Проверяем секретную фразу 1
        if secret_phrases['phrase1'] and user_text.startswith(secret_phrases['phrase1']):
            # Извлекаем текст сообщения без фразы
            content = user_text[len(secret_phrases['phrase1']):].strip()
            
            if content:  # Если есть текст после фразы
                # Формируем полное сообщение для пересылки
                forwarded_text = f"📨 *Новое сообщение*\n\n{content}\n\n_Отправлено через бота_"
                
                # Пересылаем в чат для оповещений
                await context.bot.send_message(
                    chat_id=ALERTS_CHAT_ID,
                    message_thread_id=ALERTS_THREAD_ID,
                    text=forwarded_text,
                    parse_mode=ParseMode.MARKDOWN
                )
                
                logger.info(f"Сообщение переслано в чат оповещений: {content[:50]}...")
                
                # Подтверждение пользователю
                await message.reply_text(
                    "✅ Сообщение отправлено в раздел 'Оповещения и новости'",
                    reply_to_message_id=message.message_id
                )
        
        # Проверяем секретную фразу 2
        elif secret_phrases['phrase2'] and user_text.startswith(secret_phrases['phrase2']):
            # Извлекаем текст сообщения без фразы
            content = user_text[len(secret_phrases['phrase2']):].strip()
            
            if content:  # Если есть текст после фразы
                # Формируем полное сообщение для пересылки
                forwarded_text = f"📨 *Новое сообщение*\n\n{content}\n\n_Отправлено через бота_"
                
                # Пересылаем в чат для информации
                await context.bot.send_message(
                    chat_id=INFO_CHAT_ID,
                    message_thread_id=INFO_THREAD_ID,
                    text=forwarded_text,
                    parse_mode=ParseMode.MARKDOWN
                )
                
                logger.info(f"Сообщение переслано в чат информации: {content[:50]}...")
                
                # Подтверждение пользователю
                await message.reply_text(
                    "✅ Сообщение отправлено в раздел 'Информация'",
                    reply_to_message_id=message.message_id
                )
        
        # Если сообщение не начинается с секретных фраз - игнорируем
        # (другие скрипты будут обрабатывать свои команды)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")

async def startup(application: Application):
    """Действия при запуске бота"""
    logger.info("Бот запускается...")
    
    # Генерируем и отправляем фразы сразу при запуске
    await send_daily_phrases(application)

def main():
    """Основная функция запуска бота"""
    try:
        # Проверяем наличие необходимых переменных
        if not all([TOKEN, ADMIN_CHAT_ID, ALERTS_CHAT_ID, INFO_CHAT_ID]):
            raise ValueError("Не все необходимые переменные окружения заданы!")
        
        # Создаем приложение
        application = Application.builder().token(TOKEN).build()
        
        # Добавляем обработчик сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Настраиваем ежедневную отправку фраз в 09:00
        job_queue = application.job_queue
        if job_queue:
            # Отправляем сразу при запуске
            job_queue.run_once(send_daily_phrases, when=1)
            
            # И затем каждый день в 09:00
            job_queue.run_daily(
                send_daily_phrases,
                time=time(hour=9, minute=0, second=0),
                days=(0, 1, 2, 3, 4, 5, 6),
                name="daily_phrases"
            )
        
        # Запускаем бота
        logger.info("Бот запущен и ожидает сообщений...")
        application.run_polling(allowed_updates=["message"])
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise

if __name__ == '__main__':
    main()