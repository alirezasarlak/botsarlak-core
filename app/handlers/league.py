from telegram.ext import ConversationHandler, MessageHandler, filters

from app.constants import back_home_rx, btn_rx
from app.keyboards import main_menu
from app.services.league import get_board
from app.utils.formatting import format_board


async def entry(update, context):
    board = get_board()
    await update.message.reply_text(format_board(board), reply_markup=main_menu())
    return ConversationHandler.END


league_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(btn_rx("لیگ", "🏆")), entry)],
    states={},
    fallbacks=[MessageHandler(filters.Regex(back_home_rx()), entry)],
)
