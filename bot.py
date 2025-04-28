import os
import asyncio
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)

def log_to_fluentd(data):
    print("[BOT] Sending to Fluentd:", data)
    try:
        resp = requests.post(
            "http://localhost:8080/telegram_bot",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        print(f"[BOT] Fluentd responded: {resp.status_code}")
        if not resp.ok:
            print(f"[BOT] Fluentd error: {resp.text}")
    except Exception as e:
        print(f"[BOT] Exception sending log: {e}")

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hi! I’m your Telegram bot.")

async def echo(update: Update, context: CallbackContext):
    if not (update.message and update.message.from_user and update.message.text):
        return

    user = update.message.from_user
    user_info = {
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "text": update.message.text,
        "chat_id": update.message.chat.id,
    }

    await update.message.reply_text(f"You sent: {update.message.text}")

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, log_to_fluentd, user_info)

async def error_handler(update: object, context: CallbackContext):
    print("[ERROR]", context.error)

def main():
    token = os.getenv("TELEGRAM_TOKEN", "7556712557:AAHtG2WYcJc7adeyGnQ5JtZHAzVzOfsQmZ0")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_error_handler(error_handler)

    print("✅ Bot is starting...")
    app.run_polling()
    print("✅ Bot stopped.")

if __name__ == "__main__":
    main()
