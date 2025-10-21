from telegram.ext import ConversationHandler, MessageHandler, filters

from app.constants import back_home_rx, btn_rx
from app.keyboards import main_menu
from app.models.referrals import referral_link
from app.utils.i18n import t


async def entry(update, context):
    link = referral_link(update.effective_user.id)
    await update.message.reply_text(
        t("referral_intro", link=link), reply_markup=main_menu()
    )
    return ConversationHandler.END


referrals_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(btn_rx("دعوت", "🎁")), entry)],
    states={},
    fallbacks=[MessageHandler(filters.Regex(back_home_rx()), entry)],
)
