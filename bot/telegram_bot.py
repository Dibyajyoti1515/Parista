"""Thin Telegram client for Parista.

Forwards user messages to the backend HTTP API. This is a skeleton for
the Setup phase — full message handling is wired in the Polish phase
(task T043).
"""

import os

import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

BACKEND_URL = os.getenv("PARISTA_BACKEND_URL", "http://localhost:8000")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the user issues /start."""
    await update.message.reply_text(
        "Hi! Describe an interpersonal conflict and I'll provide a grounded, "
        "cited analysis with a suggested reply."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Forward a user's text message to the backend /api/analyze endpoint."""
    text = update.message.text
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/api/analyze",
            json={"text": text},
        )
    if response.status_code == 200:
        data = response.json()
        await update.message.reply_text(data)
    else:
        await update.message.reply_text(
            "Sorry, something went wrong while analyzing your message. Please try again."
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Forward an uploaded conversation screenshot to the backend."""
    photo = update.message.photo[-1]
    file = await photo.get_file()
    content = await file.download_as_bytearray()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/api/analyze/screenshot",
            files={"file": ("screenshot.png", bytes(content), "image/png")},
        )
    if response.status_code == 200:
        data = response.json()
        await update.message.reply_text(data)
    else:
        await update.message.reply_text(
            "Sorry, I couldn't parse that screenshot. Please try a clearer image."
        )


def main() -> None:
    """Start the Telegram bot using the token from the environment."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is required")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    app.run_polling()


if __name__ == "__main__":
    main()