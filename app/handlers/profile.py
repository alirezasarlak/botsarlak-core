from telegram.ext import ConversationHandler, MessageHandler, filters
from app.models.users import get_user, set_nickname
from app.keyboards import profile_menu, main_menu
from app.constants import STATE_PROFILE_MENU, STATE_PROFILE_NICKNAME, btn_rx, back_home_rx
from app.utils.formatting import format_profile
from app.utils.i18n import t

async def entry(update, context):
    u = get_user(update.effective_user.id)
    await update.message.reply_text(format_profile(u), reply_markup=profile_menu())
    return STATE_PROFILE_MENU

async def menu(update, context):
    if update.message.text.startswith("✏️"):
        await update.message.reply_text("نام جدید؟")
        return STATE_PROFILE_NICKNAME
    await update.message.reply_text(t("invalid"), reply_markup=main_menu())
    return ConversationHandler.END

async def setnick(update, context):
    nick = update.message.text.strip()
    if len(nick) < 2 or len(nick) > 32:
        await update.message.reply_text(t("invalid"))
        return STATE_PROFILE_NICKNAME
    set_nickname(update.effective_user.id, nick)
    await update.message.reply_text("✅ به‌روزرسانی شد.", reply_markup=main_menu())
    return ConversationHandler.END

profile_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(btn_rx("پروفایل","👤")), entry)],
    states={
        STATE_PROFILE_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
        STATE_PROFILE_NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, setnick)],
    },
    fallbacks=[MessageHandler(filters.Regex(back_home_rx()), entry)],
)
