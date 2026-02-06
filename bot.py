import os
import random
import logging
import asyncio
from datetime import datetime, time
from typing import Optional
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация из .env
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID_PHRASES = int(os.getenv('CHAT_ID_PHRASES', '-1003834583271'))  # Чат для отправки фраз
CHAT_ID_ALERTS = int(os.getenv('CHAT_ID_ALERTS', '-1003802387098'))   # Чат для оповещений
CHAT_ID_INFO = int(os.getenv('CHAT_ID_INFO', '-1003802387098'))       # Чат для информации
MESSAGE_THREAD_ALERTS = int(os.getenv('MESSAGE_THREAD_ALERTS', '376'))  # ID темы для оповещений
MESSAGE_THREAD_INFO = int(os.getenv('MESSAGE_THREAD_INFO', '377'))      # ID темы для информации

# Глобальные переменные для хранения секретных фраз
secret_phrase_1: Optional[str] = None
secret_phrase_2: Optional[str] = None
awaiting_message: Optional[str] = None  # Переменная для хранения типа ожидаемого сообщения

# Списки слов для генерации фраз
RUSSIAN_WORDS = [
    "солнечный", "быстрый", "умный", "зеленый", "тихий", "веселый", "храбрый", "свежий",
    "добрый", "ясный", "синий", "теплый", "чистый", "светлый", "яркий", "спокойный",
    "горячий", "холодный", "мокрый", "сухой", "новый", "старый", "молодой", "древний",
    "современный", "технический", "природный", "городской", "деревенский", "морской",
    "горный", "лесной", "речной", "полевой", "небесный", "звездный", "лунный", "солнечный",
    "утренний", "вечерний", "ночной", "дневной", "зимний", "весенний", "летний", "осенний"
]

def generate_secret_phrase() -> str:
    """Генерирует секретную фразу из 3 случайных слов"""
    words = random.sample(RUSSIAN_WORDS, 3)
    return " ".join(words).capitalize()

async def send_daily_phrases(context: CallbackContext) -> None:
    """Отправляет ежедневные секретные фразы в указанный чат"""
    global secret_phrase_1, secret_phrase_2
    
    # Генерируем новые фразы
    secret_phrase_1 = generate_secret_phrase()
    secret_phrase_2 = generate_secret_phrase()
    
    # Формируем сообщение
    message = (
        "🔐 *Ежедневные секретные фразы*\n\n"
        f"*Фраза №1 (для оповещений):*\n`{secret_phrase_1}`\n\n"
        f"*Фраза №2 (для информации):*\n`{secret_phrase_2}`\n\n"
        "⚠️ *Внимание:* Фразы действительны только сегодня!"
    )
    
    try:
        await context.bot.send_message(
            chat_id=CHAT_ID_PHRASES,
            text=message,
            parse_mode='Markdown'
        )
        logger.info(f"Отправлены новые фразы: {secret_phrase_1}, {secret_phrase_2}")
    except Exception as e:
        logger.error(f"Ошибка при отправке фраз: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    # Этот обработчик нужен для другого скрипта
    # Здесь можно ничего не делать или добавить минимальную логику
    pass

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик всех сообщений"""
    global awaiting_message
    
    # Если сообщение из личного чата с ботом
    if update.message and update.message.chat.type == "private":
        message_text = update.message.text
        
        # Проверяем, ожидаем ли мы сообщение для пересылки
        if awaiting_message:
            await forward_message(update, context)
            awaiting_message = None
            return
            
        # Проверяем секретные фразы
        if secret_phrase_1 and message_text.strip().startswith(secret_phrase_1):
            awaiting_message = "alerts"
            await update.message.reply_text(
                "✅ Фраза №1 распознана! Отправьте сообщение для пересылки в раздел 'Оповещения и новости'.\n"
                "Сообщение будет переслано однократно."
            )
            
        elif secret_phrase_2 and message_text.strip().startswith(secret_phrase_2):
            awaiting_message = "info"
            await update.message.reply_text(
                "✅ Фраза №2 распознана! Отправьте сообщение для пересылки в раздел 'Информация'.\n"
                "Сообщение будет переслано однократно."
            )
        else:
            # Не реагируем на другие сообщения
            pass

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Пересылает полученное сообщение в соответствующий чат"""
    global awaiting_message
    
    try:
        if awaiting_message == "alerts":
            # Пересылаем в чат для оповещений
            await context.bot.send_message(
                chat_id=CHAT_ID_ALERTS,
                message_thread_id=MESSAGE_THREAD_ALERTS,
                text=f"📢 *Оповещение*\n\n{update.message.text}",
                parse_mode='Markdown'
            )
            await update.message.reply_text("✅ Сообщение переслано в 'Оповещения и новости'")
            logger.info(f"Сообщение переслано в оповещения: {update.message.text[:50]}...")
            
        elif awaiting_message == "info":
            # Пересылаем в чат для информации
            await context.bot.send_message(
                chat_id=CHAT_ID_INFO,
                message_thread_id=MESSAGE_THREAD_INFO,
                text=f"📋 *Информация*\n\n{update.message.text}",
                parse_mode='Markdown'
            )
            await update.message.reply_text("✅ Сообщение переслано в 'Информация'")
            logger.info(f"Сообщение переслано в информацию: {update.message.text[:50]}...")
            
    except Exception as e:
        logger.error(f"Ошибка при пересылке сообщения: {e}")
        await update.message.reply_text("❌ Ошибка при пересылке сообщения")

async def initialize_phrases(application: Application) -> None:
    """Инициализирует фразы при запуске бота"""
    global secret_phrase_1, secret_phrase_2
    
    # Генерируем начальные фразы
    secret_phrase_1 = generate_secret_phrase()
    secret_phrase_2 = generate_secret_phrase()
    
    # Отправляем фразы в чат
    message = (
        "🔐 *Секретные фразы инициализированы*\n\n"
        f"*Фраза №1 (для оповещений):*\n`{secret_phrase_1}`\n\n"
        f"*Фраза №2 (для информации):*\n`{secret_phrase_2}`\n\n"
        "⚠️ *Внимание:* Фразы действительны до следующей ежедневной отправки!"
    )
    
    try:
        await application.bot.send_message(
            chat_id=CHAT_ID_PHRASES,
            text=message,
            parse_mode='Markdown'
        )
        logger.info(f"Инициализированы фразы: {secret_phrase_1}, {secret_phrase_2}")
    except Exception as e:
        logger.error(f"Ошибка при отправке начальных фраз: {e}")

async def post_init(application: Application) -> None:
    """Функция, выполняемая после инициализации бота"""
    await initialize_phrases(application)

def main() -> None:
    """Основная функция запуска бота"""
    # Создаем приложение
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Настраиваем ежедневную отправку фраз в 09:00 (можно изменить)
    job_queue = application.job_queue
    if job_queue:
        # Отправка каждый день в 09:00
        job_queue.run_daily(send_daily_phrases, time(hour=9, minute=0))
    
    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()