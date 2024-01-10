from telegram import BotCommand, Update
from chatBot.tele_bot.DBPipeline import DATABASE
# from bridge_skillz_gpt.constants import PROJECT_ROOT_PATH
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from rich.console import Console
from rich.text import Text
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.environ["client_tele_bot_token"]
console = Console()

def getWelcomeMsg():
    with open("DB/WelcomeMsg.txt", "r") as file:
        return file.read()


def printPrompt(msg, color="red",end="\n"):
    console.print(Text(msg, style=color),end=end)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username or user.full_name
    history = DATABASE.getChatHistoryByUserID(user.id)

    if not history:
        WelcomeMsg = getWelcomeMsg()
        DATABASE.insertChatHistory(user.id,username ,"assistant", WelcomeMsg)
        await update.message.reply_text(WelcomeMsg)
    else:
        await update.message.reply_text(f"Yes {user.full_name} How may I assist you ?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        Query = update.message.text.strip().lower()
        username = user.username or user.full_name

        printPrompt(f"({user.full_name}) Query    >>    {Query}")
        
        if not Query:
            print("Skipped")
            return
        if Query.lower() in ['ok']:
            return
        
        if Query == "0000":
            DATABASE.truncateTable()
            return
        if Query == "1111":
            DATABASE.deleteChatHistoryByUserID(user.id)
            return
        
        DATABASE.insertChatHistory(user.id, username, "user", Query)
        await asyncio.sleep(2)
        await context.bot.send_chat_action(chat_id=user.id, action="typing")
    except Exception as e:
        print(f"[+] Telegram Error : {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Script listener is active. Ready to receive messages.")
    # Run the bot until the user presses Ctrl-C
    app.run_polling()


def start_bot():
    main()