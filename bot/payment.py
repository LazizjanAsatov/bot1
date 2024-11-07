import requests
from telegram import Update
from telegram.ext import ContextTypes

MAKE_PAYMENT_URL = "http://localhost:8000/blog/make-payment/"

# To'lov jarayonini amalga oshirish
async def handle_make_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    plan_id = context.user_data.get('selected_plan_id')
    method_id = context.user_data.get('selected_method_id')

    if plan_id and method_id:
        payload = {
            "subscription_plan": plan_id,
            "payment_method": method_id
        }
        response = requests.post(MAKE_PAYMENT_URL + f"{telegram_id}/", json=payload)
        if response.status_code == 201:
            await update.message.reply_text("To'lov muvaffaqiyatli amalga oshirildi.")
        else:
            await update.message.reply_text("To'lov amalga oshirishda xatolik yuz berdi.")
    else:
        await update.message.reply_text("To'lov ma'lumotlarini olishda xatolik yuz berdi.")
