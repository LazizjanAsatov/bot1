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
from menu import (
    show_menu,
    add_menu_handlers,
    handle_my_account,
    handle_feedback,
    handle_support,
    handle_fill_client_card,
    handle_conduct_session
)

# Backend URLs
REGISTER_URL = "http://localhost:8000/blog/register/"
CONSENT_STATUS_URL = "http://localhost:8000/blog/consent-status/"

# Logging settings
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# /start command - Register and check consent
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    telegram_id = user.id
    username = user.username

    # Send registration request
    response = requests.post(REGISTER_URL, json={"telegram_id": telegram_id, "username": username})

    if response.status_code in [200, 201]:
        # Check consent status
        consent_status_response = requests.get(f"{CONSENT_STATUS_URL}{telegram_id}/")

        if consent_status_response.status_code == 200:
            consent_data = consent_status_response.json()
            if consent_data.get("consent_given"):
                await update.message.reply_text("Rozilik allaqachon berilgan. Obuna rejalari bilan tanishing.")
                await show_subscription_plans(update, context)
            else:
                await update.message.reply_text("Rozilik berish kerak. Iltimos, rozilikni tasdiqlang.")
        else:
            await update.message.reply_text("Rozilik holatini tekshirishda xatolik yuz berdi.")
    else:
        await update.message.reply_text("Ro'yxatdan o'tishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
        logger.error(f"Ro'yxatdan o'tishda xatolik yuz berdi. Status code: {response.status_code}")

# Main function - Start the bot
def main():
    BOT_TOKEN = "7651535038:AAGzK1HJqRsGm5h8gH7t3c6ZUIp-nxmSKVI"

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_subscription, pattern="^subscribe_"))
    app.add_handler(CallbackQueryHandler(handle_payment_method, pattern="^payment_"))
    app.add_handler(CallbackQueryHandler(show_gift_subscription, pattern="^gift_"))
    app.add_handler(CallbackQueryHandler(handle_gift_payment_method, pattern="^gift_payment_"))
    
    # Menu-related handlers
    add_menu_handlers(app)  # Adds handlers for menu and submenu options
    
    # Feedback and support
    app.add_handler(CallbackQueryHandler(handle_feedback, pattern="^feedback$"))
    app.add_handler(CallbackQueryHandler(handle_support, pattern="^support$"))
    
    # Account and session handlers
    app.add_handler(CallbackQueryHandler(handle_my_account, pattern="^my_account$"))
    app.add_handler(CallbackQueryHandler(handle_fill_client_card, pattern="^fill_client_card$"))
    app.add_handler(CallbackQueryHandler(handle_conduct_session, pattern="^conduct_session$"))

    # Text message handlers for payment details and usernames
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^\d+$'), handle_payment_details))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^\d+$'), handle_gift_payment_details))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^@\w+$'), handle_gift_username))

    logger.info("Bot ishga tushirildi")
    app.run_polling()

if __name__ == '__main__':
    main()
