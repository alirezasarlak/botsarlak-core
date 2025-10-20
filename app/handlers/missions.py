from telegram.ext import ConversationHandler, MessageHandler, filters
from app.models.missions import today_missions, finish_mission
from app.keyboards import main_menu
from app.constants import btn_rx, back_home_rx
from app.utils.i18n import t

async def entry(update, context):
    m = today_missions(update.effective_user.id)
    txt = [t("mission_intro"), ""]
    for it in m:
        txt.append(f"• {it['title']} (+{it['xp']} XP) — کد: {it['code']}")
    txt.append("\nبرای اتمام، کد مأموریت رو بفرست.")
    await update.message.reply_text("\n".join(txt), reply_markup=main_menu())
    return 1

async def complete(update, context):
    code = update.message.text.strip()
    finish_mission(update.effective_user.id, code)
    await update.message.reply_text("✅ مأموریت ثبت شد. امتیاز اضافه شد.", reply_markup=main_menu())
    return ConversationHandler.END

missions_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(btn_rx("مأموریت‌ها","🎯")), entry)],
    states={
        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, complete)]
    },
    fallbacks=[MessageHandler(filters.Regex(back_home_rx()), entry)],
)
