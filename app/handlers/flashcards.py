from telegram.ext import ConversationHandler, MessageHandler, filters

from app.constants import (
    MAJOR_SUBJECTS,
    STATE_FLASHCARD_ANSWER,
    STATE_FLASHCARD_EVALUATE,
    STATE_FLASHCARD_MENU,
    STATE_FLASHCARD_QUESTION,
    STATE_FLASHCARD_REVIEW,
    STATE_FLASHCARD_SUBJECT,
    back_home_rx,
    btn_rx,
)
from app.keyboards import flash_menu, main_menu, subject_menu
from app.models.flashcards import create_card, list_due
from app.models.users import get_user
from app.services.flashcards import schedule_review
from app.utils.i18n import t


async def entry(update, context):
    await update.message.reply_text(t("flash_intro"), reply_markup=flash_menu())
    return STATE_FLASHCARD_MENU


async def menu(update, context):
    txt = update.message.text
    if txt.startswith("➕"):
        user = get_user(update.effective_user.id)
        await update.message.reply_text(
            "درس:", reply_markup=subject_menu(MAJOR_SUBJECTS[user["major"]])
        )
        return STATE_FLASHCARD_SUBJECT
    elif txt.startswith("🔁"):
        cards = list_due(update.effective_user.id)
        if not cards:
            await update.message.reply_text(t("no_cards"), reply_markup=main_menu())
            return ConversationHandler.END
        context.user_data["cards"] = cards
        context.user_data["i"] = 0
        await update.message.reply_text(cards[0]["question"])
        return STATE_FLASHCARD_REVIEW
    else:
        await update.message.reply_text(t("invalid"), reply_markup=main_menu())
        return ConversationHandler.END


async def choose_subject(update, context):
    context.user_data["fc_subject"] = update.message.text
    await update.message.reply_text("سوال؟")
    return STATE_FLASHCARD_QUESTION


async def question(update, context):
    context.user_data["fc_q"] = update.message.text
    await update.message.reply_text("پاسخ؟")
    return STATE_FLASHCARD_ANSWER


async def answer(update, context):
    user_id = update.effective_user.id
    cid = create_card(
        user_id,
        context.user_data.pop("fc_subject"),
        context.user_data.pop("fc_q"),
        update.message.text,
    )
    schedule_review(user_id, cid, False)
    await update.message.reply_text(t("added"), reply_markup=main_menu())
    return ConversationHandler.END


async def review_show_answer(update, context):
    i = context.user_data["i"]
    cards = context.user_data["cards"]
    await update.message.reply_text("پاسخ: " + cards[i]["answer"])
    await update.message.reply_text("درست بود؟ (بله/خیر)")
    return STATE_FLASHCARD_EVALUATE


async def review_eval(update, context):
    correct = update.message.text.strip() == "بله"
    i = context.user_data["i"]
    cards = context.user_data["cards"]
    schedule_review(update.effective_user.id, cards[i]["id"], correct)
    i += 1
    if i < len(cards):
        context.user_data["i"] = i
        await update.message.reply_text(cards[i]["question"])
        return STATE_FLASHCARD_REVIEW
    await update.message.reply_text(t("done"), reply_markup=main_menu())
    return ConversationHandler.END


flashcards_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(btn_rx("فلش‌کارت‌ها", "📖")), entry)],
    states={
        STATE_FLASHCARD_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
        STATE_FLASHCARD_SUBJECT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, choose_subject)
        ],
        STATE_FLASHCARD_QUESTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, question)
        ],
        STATE_FLASHCARD_ANSWER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, answer)
        ],
        STATE_FLASHCARD_REVIEW: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, review_show_answer)
        ],
        STATE_FLASHCARD_EVALUATE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, review_eval)
        ],
    },
    fallbacks=[MessageHandler(filters.Regex(back_home_rx()), entry)],
)
