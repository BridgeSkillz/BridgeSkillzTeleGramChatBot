import sqlite3
from fastapi import APIRouter, Depends, Request
from datetime import datetime
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from bridge_skillz_gpt.server.utils.auth import authenticated
from bridge_skillz_gpt.paths import PROJECT_ROOT_PATH

ui_router = APIRouter(prefix="/v1", dependencies=[Depends(authenticated)])

favicon_router = APIRouter()


@favicon_router.get('/favicon.ico')
async def favicon():
    favicon_path = 'bridge_skillz_gpt/server/ui/favicon.ico'
    return FileResponse(favicon_path)


def format_date(value, format='%Y-%m-%d %H:%M:%S'):
    if isinstance(value, str):
        return datetime.strptime(value, format).strftime(format)
    return value


templates = Jinja2Templates(directory="bridge_skillz_gpt/server/ui/templates")
templates.env.filters['date'] = format_date


def get_db():
    conn = sqlite3.connect(PROJECT_ROOT_PATH/"DB"/"Database.sqlite")
    return conn


@ui_router.get("/data")
async def read_data(request: Request):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT userid,username FROM CHATHISTORY")
    data = cursor.fetchall()
    return templates.TemplateResponse("data.html", {"request": request, "data": data})


@ui_router.get("/data/{userid}")
async def read_user_data(request: Request, userid: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM CHATHISTORY WHERE userid=?", (userid,))
    data = cursor.fetchall()
    return templates.TemplateResponse("user_data.html", {"request": request, "data": data})
