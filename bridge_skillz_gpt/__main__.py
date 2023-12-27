# start a fastapi server with uvicorn
import uvicorn
import logging

from bridge_skillz_gpt.main import app
from bridge_skillz_gpt.settings.settings import settings

uvicorn_error = logging.getLogger("uvicorn.error")
uvicorn_error.disabled = True
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_access.disabled = True

uvicorn.run(app, host="0.0.0.0", port=settings().server.port,log_config=None)