from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# MENU main handler function
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Materiallar", callback_data="materials")],
        [InlineKeyboardButton("Hisobni to'ldirish", callback_data="recharge")],
        [InlineKeyboardButton("Obuna sovg'a qilish", callback_data="gift_subscription")],
        [InlineKeyboardButton("Mening akkauntim", callback_data="my_account")],
        [InlineKeyboardButton("Fikr-mulohaza", callback_data="feedback")],
        [InlineKeyboardButton("Qo'llab-quvvatlash", callback_data="support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Quyidagilardan birini tanlang:", reply_markup=reply_markup)

# Example sub-menu handler functions for each main button:
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

async def handle_my_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "Mening akkauntim ma'lumotlari:\n\n"
        "Aktivatsiya sanasi: ...\n"
        "Balans qoldig'i: ... so'm\n"
        "Obuna tugash vaqti: ...",
        reply_markup=reply_markup
    )

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Fikr-mulohazangizni yozib qoldiring:", reply_markup=reply_markup)

async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "Qo'llab-quvvatlash uchun murojaat qiling: support@example.com yoki +998 XX XXX XXXX",
        reply_markup=reply_markup
    )

# Function to return to main MENU
async def handle_back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await show_menu(update, context)

# Creating the Application and adding handlers
def main():
    application = Application.builder().token("YOUR_BOT_TOKEN").build()

    # Adding handlers
    application.add_handler(CommandHandler("start", show_menu))
    application.add_handler(CallbackQueryHandler(handle_materials, pattern="materials"))
    application.add_handler(CallbackQueryHandler(handle_recharge, pattern="recharge"))
    application.add_handler(CallbackQueryHandler(handle_gift_subscription, pattern="gift_subscription"))
    application.add_handler(CallbackQueryHandler(handle_my_account, pattern="my_account"))
    application.add_handler(CallbackQueryHandler(handle_feedback, pattern="feedback"))
    application.add_handler(CallbackQueryHandler(handle_support, pattern="support"))
    application.add_handler(CallbackQueryHandler(handle_back_to_menu, pattern="back_to_menu"))

    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    main()
