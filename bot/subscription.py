import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Backend URLs
SUBSCRIPTION_PLANS_URL = "http://localhost:8000/blog/subscription-plans/"
SUBSCRIBE_URL = "http://localhost:8000/blog/subscribe/"
PAYMENT_METHODS_URL = "http://localhost:8000/blog/payment-methods/"
GIFT_SUBSCRIPTION_URL = "http://localhost:8000/blog/gift-subscription/"
MAKE_PAYMENT_URL = "http://localhost:8000/blog/make-payment/"


async def show_subscription_plans(update, context: ContextTypes.DEFAULT_TYPE):
    response = requests.get(SUBSCRIPTION_PLANS_URL)
    if response.status_code == 200:
        plans = response.json()
        message = "Quyidagi obuna rejalari mavjud:\n\n"
        keyboard = []

        for plan in plans:
            message += f"{plan['name']} - {plan['price']} so'm\n"
            keyboard.append([
                InlineKeyboardButton(f"{plan['name']} sotib olish", callback_data=f"subscribe_{plan['id']}"),
                InlineKeyboardButton(f"{plan['name']} sovg'a qilish", callback_data=f"gift_{plan['id']}")
            ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.callback_query:
            await update.callback_query.message.edit_text(message, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message, reply_markup=reply_markup)
    else:
        error_message = "Obuna rejalarini olishda xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring."
        if update.callback_query:
            await update.callback_query.message.edit_text(error_message)
        else:
            await update.message.reply_text(error_message)

# Obuna tanlash va to'lov usullarini ko'rsatish
async def handle_subscription(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan_id = query.data.split("_")[1]
    context.user_data['selected_plan_id'] = plan_id

    # To'lov usullarini olish
    response = requests.get(PAYMENT_METHODS_URL)
    if response.status_code == 200:
        methods = response.json()
        message = "To'lov usulini tanlang:"
        keyboard = [[InlineKeyboardButton(method['name'], callback_data=f"payment_{method['id']}")] for method in methods]
        keyboard.append([InlineKeyboardButton("🔙 Nazad", callback_data="back_to_plans")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await query.edit_message_text("To'lov usullarini olishda xatolik yuz berdi.")

# To'lov usulini tanlash va to'lovni amalga oshirish
async def handle_payment_method(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    method_id = query.data.split("_")[1]
    context.user_data['selected_method_id'] = method_id

    await query.edit_message_text("Tanlangan to‘lov usuli bo‘yicha kerakli ma'lumotlarni kiriting:")
    context.user_data['awaiting_payment_details'] = True

# To'lov ma'lumotlarini kiritish
async def handle_payment_details(update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_payment_details'):
        telegram_id = update.message.from_user.id
        details = update.message.text
        plan_id = context.user_data.get('selected_plan_id')
        method_id = context.user_data.get('selected_method_id')

        if plan_id and method_id:
            payload = {
                "subscription_plan": plan_id,
                "payment_method": method_id,
                "transaction_id": details
            }
            response = requests.post(SUBSCRIBE_URL + f"{telegram_id}/", json=payload)
            if response.status_code == 201:
                await update.message.reply_text("Obunani muvaffaqiyatli sotib oldingiz.")
            else:
                await update.message.reply_text("Obunani sotib olishda xatolik yuz berdi.")
        else:
            await update.message.reply_text("Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
        context.user_data['awaiting_payment_details'] = False

# Sovg'a qilish uchun foydalanuvchi username'ini kiritish
async def show_gift_subscription(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan_id = query.data.split("_")[1]
    context.user_data['selected_gift_plan_id'] = plan_id
    await query.message.reply_text("Sovg‘a qilmoqchi bo‘lgan foydalanuvchingizning Telegram username’ini kiriting:")
    context.user_data['awaiting_gift_username'] = True

# Sovg'a qilish uchun to'lov usulini tanlash
async def handle_gift_username(update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_gift_username'):
        username = update.message.text
        context.user_data['gift_username'] = username
        context.user_data['awaiting_gift_username'] = False

        # To'lov usullarini olish
        response = requests.get(PAYMENT_METHODS_URL)
        if response.status_code == 200:
            methods = response.json()
            keyboard = [[InlineKeyboardButton(method['name'], callback_data=f"gift_payment_{method['id']}")] for method in methods]
            keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_plans")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("To'lov usulini tanlang:", reply_markup=reply_markup)
        else:
            await update.message.reply_text("To‘lov usullarini olishda xatolik yuz berdi.")

# Sovg'a qilish to'lov usulini tanlash va to'lov ma'lumotlarini kiritish
async def handle_gift_payment_method(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    method_id = query.data.split("_")[2]
    context.user_data['selected_gift_method_id'] = method_id

    await query.edit_message_text("Tanlangan to‘lov usuli bo‘yicha kerakli ma'lumotlarni kiriting:")
    context.user_data['awaiting_gift_payment_details'] = True

# Sovg'a qilish to'lov ma'lumotlarini kiritish
async def handle_gift_payment_details(update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_gift_payment_details'):
        telegram_id = update.message.from_user.id
        details = update.message.text
        plan_id = context.user_data.get('selected_gift_plan_id')
        method_id = context.user_data.get('selected_gift_method_id')
        recipient_username = context.user_data.get('gift_username')

        if plan_id and method_id and recipient_username:
            payload = {
                "plan_id": plan_id,
                "transaction_id": details,
                "recipient_username": recipient_username
            }
            response = requests.post(GIFT_SUBSCRIPTION_URL + f"{telegram_id}/", json=payload)
            if response.status_code == 201:
                await update.message.reply_text(f"Siz {recipient_username} foydalanuvchisiga obuna sovg‘a qildingiz.")
            else:
                await update.message.reply_text("Sovg‘a qilishda xatolik yuz berdi.")
        else:
            await update.message.reply_text("Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
        context.user_data['awaiting_gift_payment_details'] = False
