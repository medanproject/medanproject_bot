import os
import time
import sys
import subprocess
import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Memuat file .env
load_dotenv()

# Replace with your bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# GitHub URLs for update checking
GITHUB_REPO = os.getenv("GITHUB_REPO")
VERSION_URL = os.getenv("VERSION_URL")
DOWNLOAD_URL = os.getenv("DOWNLOAD_URL")

CURRENT_VERSION = "1.0"  # Sesuaikan dengan versi bot Anda saat ini

# Bot functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! Use /shutdown or /restart to control the PC.")

async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Shutting down the PC...")
    os.system("shutdown /s /t 10")  # Windows Shutdown (10s delay)

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Restarting the PC...")
    os.system("shutdown /r /t 10")  # Windows Restart (10s delay)

# Update checking and downloading functions
async def check_for_update():
    try:
        response = requests.get(VERSION_URL)
        latest_version = response.text.strip()

        if latest_version != CURRENT_VERSION:
            print(f"Update tersedia: {latest_version}. Mengunduh update...")
            await download_update()
        else:
            print("Bot sudah versi terbaru.")
    except Exception as e:
        print(f"Error mengecek update: {e}")

async def download_update():
    try:
        response = requests.get(DOWNLOAD_URL, stream=True)
        with open("bot_new.exe", "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)

        print("Update berhasil diunduh! Mengganti file lama...")
        await apply_update()
    except Exception as e:
        print(f"Error mengunduh update: {e}")

async def apply_update():
    os.rename("bot.exe", "bot_old.exe")  # Rename file lama
    os.rename("bot_new.exe", "bot.exe")  # Ganti dengan yang baru
    await restart_bot()

async def restart_bot():
    print("Restarting bot...")
    subprocess.Popen(["bot.exe"])
    sys.exit()

# Main bot and update loop
async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("shutdown", shutdown))
    application.add_handler(CommandHandler("restart", restart))

    # Start the bot
    await application.initialize()
    await application.start_polling()

    # Check for updates asynchronously every hour
    while True:
        await check_for_update()
        await asyncio.sleep(3600)  # Cek update setiap 1 jam

if __name__ == "__main__":
    asyncio.run(main())

