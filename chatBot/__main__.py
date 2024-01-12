# start a fastapi server with uvicorn
import uvicorn
import logging
import threading

from chatBot.main import app
from chatBot.settings.settings import settings
from chatBot.tele_bot.TelegramMsgReceiver import start_bot
from chatBot.tele_bot.FollowUpAndChatingMiddleware import main

# uvicorn_error = logging.getLogger("uvicorn.error")
# uvicorn_error.disabled = True
# uvicorn_access = logging.getLogger("uvicorn.access")
# uvicorn_access.disabled = True
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.ERROR)

def start_uvicorn_server():
    uvicorn.run(app, host="localhost", port=8001, log_config=None)

if __name__ == "__main__":
    # Start a thread for the FastAPI server
    server_thread = threading.Thread(target=start_uvicorn_server)
    server_thread.start()

    # Start the Telegram bot

    Responding_thread = threading.Thread(target=main)
    Responding_thread.start()
    start_bot()
    # Wait for the server thread to finish
    server_thread.join()
    # Responding_thread.join()