import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# --- Настройки ---
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Замените на токен от @BotFather

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# --- Обработчики команд ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start — приветствие."""
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n"
        "Я готов к работе. Напиши мне что-нибудь или используй /help."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help — список команд."""
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start — запустить бота\n"
        "/help — список команд\n"
        "/about — информация о боте\n\n"
        "Или просто напиши мне что-нибудь — я отвечу!"
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /about — информация о боте."""
    await update.message.reply_text(
        "Я простой Telegram-бот, написанный на Python 🐍\n"
        "Создан с помощью библиотеки python-telegram-bot."
    )


# --- Обработчик обычных сообщений ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отвечает на любое текстовое сообщение."""
    text = update.message.text.lower()

    # Простые ответы на ключевые слова
    if any(word in text for word in ["привет", "хай", "hello", "hi"]):
        reply = "Привет! Как дела? 😊"
    elif any(word in text for word in ["как дела", "как ты", "what's up"]):
        reply = "Всё отлично, спасибо! А у тебя? 😄"
    elif any(word in text for word in ["пока", "до свидания", "bye"]):
        reply = "До встречи! 👋"
    elif any(word in text for word in ["спасибо", "благодарю", "thanks"]):
        reply = "Пожалуйста! Рад помочь 🙌"
    else:
        reply = f'Ты написал: "{update.message.text}"\nЯ пока учусь отвечать на всё подряд 😅'

    await update.message.reply_text(reply)


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Реагирует на неизвестные команды."""
    await update.message.reply_text(
        "Не знаю такой команды. Попробуй /help — там список всего, что я умею."
    )


# --- Запуск бота ---

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрируем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))

    # Обработчик текстовых сообщений (не команд)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Обработчик неизвестных команд
    app.add_handler(MessageHandler(filters.COMMAND, handle_unknown))

    print("Бот запущен! Нажми Ctrl+C для остановки.")
    app.run_polling()


if __name__ == "__main__":
    main()
