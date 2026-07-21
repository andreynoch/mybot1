bash
cat > bot.py << 'EOF'
import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# --- Настройки ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 24761265
PORT = int(os.environ.get("PORT", 8080))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

CHOOSE_PROBLEM, GET_NAME, GET_PHONE, GET_DESCRIPTION = range(4)

PROBLEMS = [
    "1️⃣ Потерял доступ к кошельку",
    "2️⃣ Заблокировала биржа",
    "3️⃣ Отправил USDT не туда",
    "4️⃣ Не получается войти на биржу",
]

# --- Веб-сервер ---
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK - Bot is running!")
    def log_message(self, format, *args):
        pass

def run_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    logger.info(f"Health server started on port {PORT}")
    server.serve_forever()

# Запускаем веб-сервер ПЕРВЫМ — до всего остального
health_thread = threading.Thread(target=run_health_server, daemon=True)
health_thread.start()
logger.info("Health server thread started")

# --- Обработчики бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[p] for p in PROBLEMS]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "👋 Добро пожаловать в *CryptoRecoveryLab*!\n\n"
        "Мы помогаем восстановить доступ к криптовалютным активам.\n\n"
        "📋 Выберите вашу проблему:",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )
    return CHOOSE_PROBLEM

async def choose_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text not in PROBLEMS:
        keyboard = [[p] for p in PROBLEMS]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "Пожалуйста, выберите один из вариантов 👇",
            reply_markup=reply_markup,
        )
        return CHOOSE_PROBLEM
    context.user_data["problem"] = text
    await update.message.reply_text(
        "✅ Понял! Теперь введите ваше *имя*:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return GET_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        "📱 Введите ваш *номер телефона* или другой способ связи:",
        parse_mode="Markdown",
    )
    return GET_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text(
        "📝 Опишите вашу ситуацию подробнее (или напишите *—* если нечего добавить):",
        parse_mode="Markdown",
    )
    return GET_DESCRIPTION

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["description"] = update.message.text
    user = update.effective_user
    data = context.user_data

    await update.message.reply_text(
        "✅ *Ваша заявка принята!*\n\n"
        "Наш специалист свяжется с вами в ближайшее время.\n\n"
        "🌐 cryptorecoverylab.com",
        parse_mode="Markdown",
    )

    admin_message = (
        "🔔 *Новая заявка!*\n\n"
        f"👤 *Пользователь:* {user.full_name}\n"
        f"🔗 *Username:* @{user.username if user.username else 'не указан'}\n"
        f"🆔 *Telegram ID:* `{user.id}`\n\n"
        f"❗ *Проблема:* {data.get('problem')}\n\n"
        f"📛 *Имя:* {data.get('name')}\n"
        f"📱 *Контакт:* {data.get('phone')}\n"
        f"📝 *Описание:* {data.get('description')}\n"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_message,
        parse_mode="Markdown",
    )
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Заявка отменена. Напишите /start чтобы начать заново.",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END

# --- Запуск ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_problem)],
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            GET_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)
    print("Бот запущен! Нажми Ctrl+C для остановки.")
    app.run_polling()

if __name__ == "__main__":
    main()
EOF
Output
exit code 0
