from telegram import Update
from telegram.ext import ContextTypes
import requests
from consent import ask_for_consent  # Rozilik funksiyasini import qilamiz

# Backenddagi ro‘yxatdan o‘tish endpoint manzili
REGISTER_URL = "http://localhost:8000/blog/register/"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    username = user.username or user.first_name  # username mavjud bo'lmasa, foydalanuvchi ismini olamiz

    await update.message.reply_text("Assalomu alaykum! Ro‘yxatdan o‘tish jarayonini boshlaymiz.")

    try:
        # Ro'yxatdan o'tish ma'lumotlarini backendga yuborish
        response = requests.post(REGISTER_URL, json={"telegram_id": telegram_id, "username": username})

        # Backenddan kelgan javobni tekshirish
        if response.status_code == 201:
            message = "Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz."
            await update.message.reply_text(message)

            # Ro'yxatdan o'tgandan so'ng avtomatik ravishda rozilikni so'rash
            await ask_for_consent(update, context)

        elif response.status_code == 200:
            message = "Siz allaqachon ro‘yxatdan o‘tgan ekansiz."
            await update.message.reply_text(message)

            # Agar foydalanuvchi allaqachon ro'yxatdan o'tgan bo'lsa ham rozilik so'rashni takrorlaymiz
            await ask_for_consent(update, context)

        else:
            message = f"Ro'yxatdan o'tishda xatolik yuz berdi. Status: {response.status_code}, Xato: {response.text}"
            await update.message.reply_text(message)

    except requests.exceptions.RequestException as e:
        message = f"Backendga ulanishda xatolik: {e}"
        await update.message.reply_text(message)
