import asyncio
import os

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

load_dotenv()


async def main():
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    await app.bot.send_message(
        int(os.getenv("ADMIN_ID")), "✅ SarlakBot v6.1 is online"
    )


if __name__ == "__main__":
    asyncio.run(main())
