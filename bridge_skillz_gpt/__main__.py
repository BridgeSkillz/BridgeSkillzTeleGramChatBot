# start a fastapi server with uvicorn
import uvicorn
import logging
import asyncio

from bridge_skillz_gpt.main import app
from bridge_skillz_gpt.settings.settings import settings
from bridge_skillz_gpt.tele_bot.BridgeSKillzBot import start_bot
import threading

uvicorn_error = logging.getLogger("uvicorn.error")
uvicorn_error.disabled = True
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_access.disabled = True

async def start_uvicorn_server():
    uvicorn.run(app, host="0.0.0.0", port=settings().server.port,log_config=None)

def start_uvicorn_server():
    uvicorn.run(app, host="0.0.0.0", port=settings().server.port,log_config=None)

if __name__ == "__main__":
    # Start a thread for the FastAPI server
    server_thread = threading.Thread(target=start_uvicorn_server)
    server_thread.start()

    # Start the Telegram bot
    start_bot()

    # Wait for the server thread to finish
    server_thread.join()