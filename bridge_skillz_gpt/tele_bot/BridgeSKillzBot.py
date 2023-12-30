from openai import OpenAI
from telegram import BotCommand, Update
from bridge_skillz_gpt.tele_bot.BridgeSkillzBotBrain import BRAIN
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
    with open("bridge_skillz_gpt/tele_bot/persona.txt", "r") as file:
        return file.read()


def printPrompt(msg, color="red"):
    console.print(Text(msg, style=color))


SYSTEMPROMPT = [{"role": "system", "content": getSystemPrompt()}]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username
    history = BRAIN.getChatHistoryByUserID(user.id)
    if not history:
        WelcomeMsg = "Welcome to oooom.in, my name is Acharya Aswini Kumar (Acharya). How may I assist you today?"
        BRAIN.insertChatHistory(user.id, username, "assistant", WelcomeMsg)
        await update.message.reply_text(WelcomeMsg)
    else:
        await update.message.reply_text(f"Yes {user.full_name} How may I assist you ?")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    Query = update.message.text

    username = user.username

    if not Query:
        return
    printPrompt(f"({user.full_name}) Query    >>    {Query}")
    BRAIN.insertChatHistory(user.id, username, "user", Query)

    Query = "Reply in 10 Words : " + Query
    ChatHistory = SYSTEMPROMPT + BRAIN.getChatHistoryByUserID(user.id)

    await update.effective_chat.send_action(constants.ChatAction.TYPING)

    Response = ""
    while not Response:
        Response = MODEL.chat.completions.create(
            model="local-model",
            messages=ChatHistory,
            temperature=0.7,
        )
        Response = Response.choices[0].message.content
        Response = (
            Response.replace("[INST", " ")
            .replace("[/INST]", " ")
            .replace("[/INST", " ")
        )
    printPrompt(f"({user.full_name}) Response >>    {Response}", "blue")
    BRAIN.insertChatHistory(user.id, username, "assistant", Response)
    print("\n\n")
    await update.message.reply_text(Response)


async def post_init(application: Application):
    """sets the bot commands in the telegram bot, these commands shows in hamburger menu"""

    command_description = {"start": "Start your conversation with Acharya"}

    commands = [
        # BotCommand(command="start", description=command_description["start"]),
        # BotCommand(command='help', description=command_description['help']),
    ]
    await application.bot.set_my_commands(commands)


def main():
    # Create the Application and pass it your bot's token.
    app = ApplicationBuilder().token(TOKEN).post_init(
        post_init).concurrent_updates(False).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    app.run_polling()


def start_bot():
    main()


if __name__ == "__main__":
    main()
