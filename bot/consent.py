import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

CONSENT_URL = "http://localhost:8000/blog/consent/"  # To'g'ri URL

async def ask_for_consent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ Rozilik beraman", callback_data="consent_accept")],
        [InlineKeyboardButton("❌ Rad etish", callback_data="consent_decline")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Hurmatli foydalanuvchi! Botdan foydalanishdan oldin hujjatlar bilan tanishib chiqishingiz va rozilik berishingiz lozim.",
        reply_markup=reply_markup
    )

async def handle_consent_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "consent_accept":
        telegram_id = query.from_user.id
        response = requests.post(f"{CONSENT_URL}{telegram_id}/", json={"telegram_id": telegram_id})

        if response.status_code == 201:
            await query.edit_message_text("Rozilik muvaffaqiyatli olindi. Endi obuna rejalari bilan tanishishingiz mumkin.")
        else:
            await query.edit_message_text("Rozilikni saqlashda xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
    else:
        await query.edit_message_text("Siz rozilik berishdan voz kechdingiz.")
