from app.utils.text_splitter import split_message


async def send_text(application, chat_id: int, text: str):
    for p in split_message(text):
        await application.bot.send_message(chat_id, p)
