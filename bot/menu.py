import asyncpg
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# Database connection function to retrieve user-specific data
async def get_user_data(user_id):
    try:
        conn = await asyncpg.connect(
            user="your_db_user", password="your_db_password",
            database="your_db_name", host="your_db_host", port="your_db_port"
        )
        query = """
            SELECT activation_date, balance, subscription_end 
            FROM users 
            WHERE telegram_id = $1
        """
        result = await conn.fetchrow(query, user_id)
        await conn.close()
        
        if result:
            return {
                "activation_date": result['activation_date'],
                "balance": result['balance'],
                "subscription_end": result['subscription_end']
            }
    except Exception as e:
        print(f"Database error: {e}")
    return None

# Asynchronous function to save messages
async def save_message(user_id, message_text, message_type):
    try:
        conn = await asyncpg.connect(
            user="your_db_user", password="your_db_password",
            database="your_db_name", host="your_db_host", port="your_db_port"
        )
        query = """
            INSERT INTO user_messages (user_id, message, message_type, timestamp)
            VALUES ($1, $2, $3, NOW())
        """
        await conn.execute(query, user_id, message_text, message_type)
        await conn.close()
    except Exception as e:
        print(f"Database error when saving message: {e}")

# Show main menu
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Materiallar", callback_data="materials")],
        [InlineKeyboardButton("Hisobni to'ldirish", callback_data="recharge")],
        [InlineKeyboardButton("Obuna sovg'a qilish", callback_data="gift_subscription")],
        [InlineKeyboardButton("Mening akkauntim", callback_data="my_account")],
        [InlineKeyboardButton("Fikr-mulohaza", callback_data="feedback")],
        [InlineKeyboardButton("Qo'llab-quvvatlash", callback_data="support")],
        [InlineKeyboardButton("Mijoz kartasini to'ldirish", callback_data="fill_client_card")],
        [InlineKeyboardButton("Seansni o'tkazish", callback_data="conduct_session")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Quyidagilardan birini tanlang:", reply_markup=reply_markup)

# Sub-menu handlers
async def handle_materials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Metodik qo'llanma", callback_data="methodical_manual")],
        [InlineKeyboardButton("Ishchi daftarlar", callback_data="workbooks")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Materiallar bo'limidan birini tanlang:", reply_markup=reply_markup)

async def handle_recharge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("To'lov usullari", callback_data="payment_options")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Hisobni to'ldirish bo'limidan birini tanlang:", reply_markup=reply_markup)

async def handle_gift_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Telegram nikni tanlash", callback_data="select_username")],
        [InlineKeyboardButton("To'lov usullari", callback_data="gift_payment_options")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Obunani sovg'a qilish uchun quyidagilardan birini tanlang:", reply_markup=reply_markup)

# Handle user's account information
async def handle_my_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data = await get_user_data(user_id)
    
    if user_data:
        account_info = (
            f"Mening akkauntim ma'lumotlari:\n\n"
            f"Aktivatsiya sanasi: {user_data['activation_date']}\n"
            f"Balans qoldig'i: {user_data['balance']} so'm\n"
            f"Obuna tugash vaqti: {user_data['subscription_end']}"
        )
    else:
        account_info = "Kechirasiz, akkaunt ma'lumotlari topilmadi."

    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(account_info, reply_markup=reply_markup)

# Feedback and support handlers
async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['awaiting_feedback'] = True
    context.user_data['awaiting_support'] = False
    
    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Fikr-mulohazangizni yozib qoldiring:", reply_markup=reply_markup)

async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['awaiting_feedback'] = False
    context.user_data['awaiting_support'] = True
    
    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Qo'llab-quvvatlash uchun murojaat qiling: support@example.com yoki +998 XX XXX XXXX", reply_markup=reply_markup)

# Message handler to save feedback/support
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    message_text = update.message.text
    message_type = "feedback" if context.user_data.get('awaiting_feedback') else "support" if context.user_data.get('awaiting_support') else None
    
    if message_type:
        await save_message(user_id, message_text, message_type)
        await update.message.reply_text("Xabaringiz qabul qilindi.")
        context.user_data['awaiting_feedback'] = False
        context.user_data['awaiting_support'] = False

# Additional options
async def handle_fill_client_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Mijoz kartasini to'ldirish tanlandi.")

async def handle_conduct_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Seansni o'tkazish tanlandi.")

# Back to main menu
async def handle_back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await show_menu(query, context)

# Add handlers to the application
def add_menu_handlers(application):
    application.add_handler(CallbackQueryHandler(handle_materials, pattern="materials"))
    application.add_handler(CallbackQueryHandler(handle_recharge, pattern="recharge"))
    application.add_handler(CallbackQueryHandler(handle_gift_subscription, pattern="gift_subscription"))
    application.add_handler(CallbackQueryHandler(handle_my_account, pattern="my_account"))
    application.add_handler(CallbackQueryHandler(handle_feedback, pattern="feedback"))
    application.add_handler(CallbackQueryHandler(handle_support, pattern="support"))
    application.add_handler(CallbackQueryHandler(handle_fill_client_card, pattern="fill_client_card"))
    application.add_handler(CallbackQueryHandler(handle_conduct_session, pattern="conduct_session"))
    application.add_handler(CallbackQueryHandler(handle_back_to_menu, pattern="back_to_menu"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))
