# main.py
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from subscription import (
    show_subscription_plans,
    handle_subscription,
    handle_payment_method,
    handle_payment_details,
    show_gift_subscription,
    handle_gift_username,
    handle_gift_payment_method,
    handle_gift_payment_details
)
from payment import handle_make_payment
from menu import show_menu, add_menu_handlers

# Backend URL'larini to'g'ridan-to'g'ri aniqlash
REGISTER_URL = "http://localhost:8000/blog/register/"
CONSENT_STATUS_URL = "http://localhost:8000/blog/consent-status/"

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# /start komandasi - Ro'yxatdan o'tish va rozilik so'rash
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user = update.message.from_user
    telegram_id = user.id
    username = user.username

    # Ro'yxatdan o'tish uchun backendga so'rov yuborish
    response = requests.post(REGISTER_URL, json={"telegram_id": telegram_id, "username": username})

    if response.status_code in [200, 201]:
        # Rozilik holatini tekshirish
        consent_status_response = requests.get(f"{CONSENT_STATUS_URL}{telegram_id}/")

        if consent_status_response.status_code == 200:
            consent_data = consent_status_response.json()
            if consent_data.get("consent_given"):
                await update.message.reply_text("Rozilik allaqachon berilgan. Obuna rejalari bilan tanishing.")
                await show_subscription_plans(update, context)  # To'g'ridan-to'g'ri obuna rejalari qismiga o'tamiz
            else:
                await update.message.reply_text("Rozilik berish kerak. Iltimos, rozilikni tasdiqlang.")
        else:
            await update.message.reply_text("Rozilik holatini tekshirishda xatolik yuz berdi.")
    else:
        await update.message.reply_text("Ro'yxatdan o'tishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
        logger.error(f"Ro'yxatdan o'tishda xatolik yuz berdi. Status code: {response.status_code}")



# Asosiy funksiya - Botni ishga tushirish
def main():
    BOT_TOKEN = "7651535038:AAGzK1HJqRsGm5h8gH7t3c6ZUIp-nxmSKVI"

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Komanda handlerlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_subscription, pattern="^subscribe_"))
    app.add_handler(CallbackQueryHandler(handle_payment_method, pattern="^payment_"))
    app.add_handler(CallbackQueryHandler(show_gift_subscription, pattern="^gift_"))
    app.add_handler(CallbackQueryHandler(handle_gift_payment_method, pattern="^gift_payment_"))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^\d+$'), handle_payment_details))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^\d+$'), handle_gift_payment_details))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^@\w+$'), handle_gift_username))

    logger.info("Bot ishga tushirildi")
    app.run_polling()

if __name__ == '__main__':
    main()
