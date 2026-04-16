# -*- coding: utf-8 -*-
import time
import sys
import io
import os
import json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

user_last_message = {}
# BOT TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID")) # Apna actual ID yahan daalo

# Channels list
ALLOWED_CHANNELS = [
    {"name": "EVOFOX",            "link": "https://t.me/+L5XdykmRJQljZTVl"},
    {"name": "LOOTS BY ULTRON",   "link": "https://t.me/LOOTSBY53"},
    {"name": "Gift Codes Looters","link": "https://t.me/GiftCodes_Looters"},
]
async def channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = []
    
    for channel in ALLOWED_CHANNELS:
        buttons.append([InlineKeyboardButton(channel["name"], url=channel["link"])])

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "📢 Hamare Official Channels:\n\n👇 Join karo:",
        reply_markup=reply_markup
    )

# User save/load
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
    return {
        "total_users": len(users)
    } 

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    await update.message.reply_text(
        "👋 Welcome! Mujhe hii bhejo Aur pao mauka paise kamane ka!!"
    )

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 Help Menu\n\n"
        "📌 Commands:\n"
        "/start - Bot shuru karo\n"
        "/help - Yeh menu dekho\n"
        "/channels - Channels ki list dekho\n\n"
        "💬 Ya bas hii likho aur channels pao!\n\n"
        "❓ Koi problem? Contact karo: @bTan_09"
    )

# /channels
async def channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "📢 Hamare Official Channels join Now!:\n\n"
    for channel in ALLOWED_CHANNELS:
        message += f"📢 {channel['name']} - {channel['link']}\n\n"
    message += "❤️ react karo aur Channels ke liye! 🚀"
    await update.message.reply_text(
        message,
        disable_web_page_preview=True
    )

# /users
async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    stats = get_stats()

    await update.message.reply_text(
        f"📊 Bot Stats:\n\n"
        f"👥 Total Users: {stats['total_users']}"
    )

#/menu command
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🤖 Bot Features Menu\n\n"
        "📌 /start - Start bot\n"
        "📢 /channels - Join channels\n"
        "🆘 /help - Help menu\n\n"
        "💬 Smart replies:\n"
        "• hi / hello → channels\n"
        "• earn / paise → earning info\n"
        "• link → channel list\n\n"
        "🚀 Type commands to use features!"
    )

    await update.message.reply_text(message)
# hii handler
async def handle_hii(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_time = time.time()

    if user_id in user_last_message:
        if current_time - user_last_message[user_id] < 5:
            return  # ignore spam

    user_last_message[user_id] = current_time

    save_user(user_id)

    user_name = update.effective_user.first_name or "Friend"
    message = f"👋 Hello {user_name}! Ye raha khajana:\n\n"

    for channel in ALLOWED_CHANNELS:
        message += f"📢 {channel['name']} - {channel['link']}\n\n"

    await update.message.reply_text(message)

# greetings handler
async def handle_greetings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_hii(update, context)

async def smart_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "earn" in text or "paise" in text:
        await update.message.reply_text("💰 Paise kamane ke liye channels join karo! /channels")

    elif "help" in text:
        await help_command(update, context)

    elif "link" in text:
        await channels_command(update, context) 

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: /broadcast message")
        return

    message = " ".join(context.args)
    users = load_users()

    success = 0
    failed = 0

    for user in users:
        try:
            await context.bot.send_message(chat_id=user, text=message)
            success += 1
        except:
            failed += 1

    await update.message.reply_text(
        f"✅ Broadcast Done\n\n"
        f"✔️ Sent: {success}\n"
        f"❌ Failed: {failed}"
    )
# Main
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("channels", channels_command))
    app.add_handler(CommandHandler("users", users_command))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("menu", menu_command))

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"(?i)^hi+$"), handle_hii))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"(?i)^(hello|hey|namaste|helo|hlo|hlw|hayy)$"), handle_greetings))

# KEEP THIS LAST
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_reply))
    print("Bot chal raha hai... (Ctrl+C se band karo)")
    app.run_polling()

if __name__ == "__main__":
    main()
