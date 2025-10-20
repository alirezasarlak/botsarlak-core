from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from app.models.users import ensure_user, get_user, set_major, set_nickname, set_phone
from app.keyboards import main_menu, major_menu
from app.constants import (
    STATE_START_MAJOR, STATE_START_NICKNAME, STATE_START_PHONE, MAJOR_SUBJECTS, btn_rx, back_home_rx
)
from app.utils.i18n import t

async def start(update, context):
    u = update.effective_user
    ensure_user(u.id, u.username, u.first_name, u.last_name)
    data = get_user(u.id)
    if not data.get("major"):
        await update.message.reply_text(t("pick_major"), reply_markup=major_menu(list(MAJOR_SUBJECTS.keys())))
        return STATE_START_MAJOR
    await update.message.reply_text(t("welcome"), reply_markup=main_menu())
    return ConversationHandler.END

async def handle_major(update, context):
    major = update.message.text
    if major not in MAJOR_SUBJECTS:
        await update.message.reply_text(t("invalid"))
        return STATE_START_MAJOR
    set_major(update.effective_user.id, major)
    await update.message.reply_text(t("enter_nickname"))
    return STATE_START_NICKNAME

async def handle_nickname(update, context):
    nick = update.message.text.strip()
    if len(nick) < 2 or len(nick) > 32:
        await update.message.reply_text(t("invalid"))
        return STATE_START_NICKNAME
    set_nickname(update.effective_user.id, nick)
    await update.message.reply_text(t("enter_phone"))
    return STATE_START_PHONE

async def handle_phone(update, context):
    phone = update.message.text.strip()
    if not (phone.startswith("09") and len(phone)==11 and phone.isdigit()):
        await update.message.reply_text(t("invalid"))
        return STATE_START_PHONE
    set_phone(update.effective_user.id, phone)
    await update.message.reply_text(t("registered"), reply_markup=main_menu())
    return ConversationHandler.END

start_conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        STATE_START_MAJOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_major)],
        STATE_START_NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_nickname)],
        STATE_START_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)],
    },
    fallbacks=[MessageHandler(filters.Regex(back_home_rx()), start)],
)
