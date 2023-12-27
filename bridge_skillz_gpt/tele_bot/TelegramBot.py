from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import os
from dotenv import load_dotenv
client = OpenAI(base_url="http://localhost:8001/v1",
                api_key="gybf6btr9j993bg6g")
load_dotenv()

TOKEN = os.environ['tele_bot_token']

SystemString = """
Response as a Bikram, always answer in 10 to 15 words 
"""
with open("bridge_skillz_gpt\\tele_bot\persona.txt", "r") as file:
    SystemString += file.read()

msgs = [
    {"role": "system", "content": SystemString},
    # {"role":"assistant","content":"Hello! 👋 Welcome to Bridgeskillz. I'm Bikram from Sales Team. \nFirst, may I have your name? It's great to address you personally."}
]

TempDB = dict()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    UserName = user.first_name+" "+user.last_name
    TempDB[f"{user.id}"] = dict(name=UserName, history=msgs)
    await update.message.reply_text("Hello! 👋 Welcome to Bridgeskillz. I'm Bikram from Sales Team.")
    await update.message.reply_text("First, may I have your name? It's great to address you personally.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Respond to a regular message with the user's ID and name."""
    user = update.effective_user
    text = update.message.text
    if user:
        UserName = user.first_name+" "+user.last_name
        user_id = user.id

        if f"{user_id}" in TempDB:
            TempDB[f"{user_id}"]['history'].append(
                {"role": "user", "content": text})
            chats = TempDB[f'{user_id}']['history']
            print(f"[+] User ({UserName}) : {text}")
            completion = client.chat.completions.create(
                model="local-model",  # this field is currently unused
                messages=chats,
                temperature=0.7,
            )
            resp = completion.choices[0].message.content
            print(f"[+] Assistant  : {resp}\n\n")

            TempDB[f"{user_id}"]['history'].append(
                {"role": "assistant", "content": resp})
            await update.message.reply_text(resp)

    else:
        user = update.effective_user
        UserName = user.first_name+" "+user.last_name
        TempDB[f"{user.id}"] = dict(name=UserName, history=msgs)
        await update.message.reply_text("Hello! 👋 Welcome to Bridgeskillz. I'm Bikram from Sales Team.")
        await update.message.reply_text("First, may I have your name? It's great to address you personally.")

app = ApplicationBuilder().token(TOKEN).build()

# Add handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
