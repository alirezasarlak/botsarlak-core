from telegram.ext import ConversationHandler, MessageHandler, filters
from app.models.users import get_user
from app.services.reports import start_report, finalize_report
from app.keyboards import subject_menu, main_menu
from app.constants import (
    STATE_REPORT_SUBJECT, STATE_REPORT_TOPIC, STATE_REPORT_TESTS, STATE_REPORT_NOTES,
    MAJOR_SUBJECTS, btn_rx, back_home_rx
)
from app.utils.i18n import t

async def entry(update, context):
    user = get_user(update.effective_user.id)
    context.user_data['session_id'] = start_report(user['id'])
    context.user_data['entries'] = []
    await update.message.reply_text(t("report_subject"), reply_markup=subject_menu(MAJOR_SUBJECTS[user['major']]))
    return STATE_REPORT_SUBJECT

async def subject(update, context):
    context.user_data['e'] = {'subject': update.message.text}
    await update.message.reply_text(t("report_topic"))
    return STATE_REPORT_TOPIC

async def topic(update, context):
    context.user_data['e']['topic'] = update.message.text
    await update.message.reply_text(t("report_tests"))
    return STATE_REPORT_TESTS

async def tests(update, context):
    try:
        tests = int(update.message.text)
    except:
        await update.message.reply_text(t("invalid")); return STATE_REPORT_TESTS
    context.user_data['e']['tests'] = tests
    await update.message.reply_text(t("report_notes"))
    return STATE_REPORT_NOTES

async def notes(update, context):
    e = context.user_data.pop('e')
    e['notes'] = update.message.text
    e['dur'] = 60  # نمونه — در v6.2 تایمر زنده اضافه می‌شود
    context.user_data['entries'].append(e)
    total_dur, total_tests, pts = await finalize(update, context)
    await update.message.reply_text(t("report_summary", dur=total_dur, tests=total_tests, pts=pts), reply_markup=main_menu())
    return ConversationHandler.END

async def finalize(update, context):
    session_id = context.user_data.pop('session_id')
    entries = context.user_data.pop('entries')
    total_dur, total_tests, pts = finalize_report(update.effective_user.id, session_id, entries)
    return total_dur, total_tests, pts

report_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(btn_rx("گزارش کار","📝")), entry)],
    states={
        STATE_REPORT_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, subject)],
        STATE_REPORT_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, topic)],
        STATE_REPORT_TESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, tests)],
        STATE_REPORT_NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, notes)],
    },
    fallbacks=[MessageHandler(filters.Regex(back_home_rx()), entry)],
)
