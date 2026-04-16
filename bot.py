# -*- coding: utf-8 -*-
import time
import os
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

user_last_message = {}

# =========================
# ENV VARIABLES (SAFE)
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = os.getenv("ADMIN_ID")
ADMIN_ID = int(ADMIN_ID) if ADMIN_ID and ADMIN_ID.isdigit() else 0

# =========================
# CHANNELS
# =========================
ALLOWED_CHANNELS = [
    {"name": "EVOFOX", "link": "https://t.me/+L5XdykmRJQljZTVl"},
    {"name": "LOOTS BY ULTRON", "link": "https://t.me/LOOTSBY53"},
    {"name": "Gift Codes Looters", "link": "https://t.me/GiftCodes_Looters"},
]

# =========================
# USERS FILE SAFE HANDLING
# =========================
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open("users.json", "w") as f:
            json.dump(users, f)

def get_stats():
    users = load_users()
    return {"total_users": len(users)}

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)

    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "👉 Type /menu to see all features of this bot."
    )

# =========================
# HELP
# =========================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 Help Menu\n\n"
        "/start - Start bot\n"
        "/menu - Features list\n"
        "/channels - Join channels\n"
        "/help - Help menu\n"
    )

# =========================
# MENU
# =========================
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Features Menu\n\n"
        "📌 /start - Start bot\n"
        "📢 /channels - Join channels\n"
        "🆘 /help - Help menu\n\n"
        "💬 Smart replies:\n"
        "• hi / hello → channels\n"
        "• earn / paise → earning info\n"
        "• link → channel list\n"
    )

# =========================
# CHANNELS
# =========================
async def channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "📢 Official Channels:\n\n"

    for c in ALLOWED_CHANNELS:
        message += f"📢 {c['name']} - {c['link']}\n\n"

    await update.message.reply_text(
        message,
        disable_web_page_preview=True
    )

# =========================
# USERS (ADMIN ONLY)
# =========================
async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    stats = get_stats()

    await update.message.reply_text(
        f"📊 Bot Stats\n\n👥 Total Users: {stats['total_users']}"
    )

# =========================
# HI HANDLER (ANTI-SPAM)
# =========================
async def handle_hii(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()

    if user_id in user_last_message:
        if now - user_last_message[user_id] < 5:
            return

    user_last_message[user_id] = now
    save_user(user_id)

    name = update.effective_user.first_name or "Friend"

    msg = f"👋 Hello {name}!\n\n📢 Join channels:\n\n"

    for c in ALLOWED_CHANNELS:
        msg += f"{c['name']} - {c['link']}\n\n"

    await update.message.reply_text(msg)

# =========================
# SMART REPLY
# =========================
async def smart_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").lower()

    if "earn" in text or "paise" in text:
        await update.message.reply_text("💰 Earn info: /channels")

    elif "help" in text:
        await help_command(update, context)

    elif "link" in text:
        await channels_command(update, context)

# =========================
# BROADCAST (ADMIN ONLY)
# =========================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast message")
        return

    message = " ".join(context.args)
    users = load_users()

    success = 0
    failed = 0

    for u in users:
        try:
            await context.bot.send_message(chat_id=u, text=message)
            success += 1
        except:
            failed += 1

    await update.message.reply_text(
        f"Broadcast Done\n✔️ {success}\n❌ {failed}"
    )

# =========================
# MAIN
# =========================
def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN missing!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("channels", channels_command))
    app.add_handler(CommandHandler("users", users_command))
    app.add_handler(CommandHandler("broadcast", broadcast))

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"(?i)^hi+$"), handle_hii))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"(?i)^(hello|hey|namaste|helo|hlo|hlw|hayy)$"), handle_hii))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_reply))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
