from telegram.ext import ConversationHandler, MessageHandler, filters
from app.config import Config
from app.keyboards import main_menu
from app.utils.i18n import t
from app.constants import btn_rx, back_home_rx

async def entry(update, context):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text(t("admin_denied"), reply_markup=main_menu())
        return ConversationHandler.END
    await update.message.reply_text(t("admin_menu"), reply_markup=main_menu())
    return ConversationHandler.END

admin_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(btn_rx("پنل ادمین","🛠")), entry)],
    states={},
    fallbacks=[MessageHandler(filters.Regex(back_home_rx()), entry)],
)
