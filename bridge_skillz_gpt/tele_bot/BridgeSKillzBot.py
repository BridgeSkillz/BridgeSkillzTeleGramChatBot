import asyncio
from openai import OpenAI
from telegram import BotCommand, Update
from bridge_skillz_gpt.tele_bot.BridgeSkillzBotBrain import BRAIN
from bridge_skillz_gpt.constants import PROJECT_ROOT_PATH
from telegram.ext import (
    ApplicationBuilder,
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram import constants
from rich.console import Console
from rich.text import Text
import os
from dotenv import load_dotenv
import logging


load_dotenv()

https_logger = logging.getLogger("httpx")
https_logger.disabled = True

TOKEN = os.environ["client_tele_bot_token"]
console = Console()

MODEL = OpenAI(base_url="http://localhost:8001/v1",
               api_key="gybf6btr9j993bg6g")


def getSystemPrompt():
    with open(PROJECT_ROOT_PATH/"DB"/"BotBehaviour.txt", "r") as file:
        return file.read()


def getWelcomeMsg():
    with open(PROJECT_ROOT_PATH/"DB"/"WelcomeMsg.txt", "r") as file:
        return file.read()


def getCommunicationRules():
    with open(PROJECT_ROOT_PATH/"DB"/"RulesAndRegulationForResponse.txt", "r") as file:
        return file.read()


def printPrompt(msg, color="red"):
    console.print(Text(msg, style=color))


SYSTEMPROMPT = [{"role": "system", "content": getSystemPrompt()}, {
    "role": "user", "content": "Hii"}]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username
    if not username:
        username = user.full_name
    history = BRAIN.getChatHistoryByUserID(user.id)
    if not history:
        WelcomeMsg = getWelcomeMsg()
        BRAIN.insertChatHistory(user.id,username ,"assistant", WelcomeMsg)
        await update.message.reply_text(WelcomeMsg)
    else:
        await update.message.reply_text(f"Yes {user.full_name} How may I assist you ?")


Suffix = getCommunicationRules()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        Query = update.message.text
        username = user.username
        if not username:
            username = user.full_name

        Response = ""
        if not Query:
            return

        printPrompt(f"({user.full_name}) Query    >>    {Query}")

        ChatHistory = SYSTEMPROMPT + BRAIN.getChatHistoryByUserID(
            user.id) + [{"role": "user", "content": Query + f"({Suffix})"}]

        while not Response:
            Response = MODEL.chat.completions.create(
                model="local-model",
                messages=ChatHistory,
                temperature=0.5,
            )
            Response = Response.choices[0].message.content
            Response = (
                Response.replace("[INST", " ")
                .replace("[/INST]", " ")
                .replace("[/INST", " ")
            )
        printPrompt(f"({user.full_name}) Response >>    {Response}", "blue")
        username = user.username
        BRAIN.insertChatHistory(user.id, username, "user", Query)
        BRAIN.insertChatHistory(user.id, username, "assistant", Response)
        print("\n\n")

        for line in Response.split("\n"):
            if line:
                await update.message.reply_text(Response)
                await asyncio.sleep(2)
    except Exception as e:
        print(f"[+] Error : {e}")
    # pass


def main():
    # Create the Application and pass it your bot's token.
    app = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    app.run_polling()


def start_bot():
    main()
