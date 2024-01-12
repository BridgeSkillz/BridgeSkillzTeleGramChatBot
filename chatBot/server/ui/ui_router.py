import sqlite3
from fastapi import APIRouter, Depends, Request
from datetime import datetime
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from chatBot.server.utils.auth import authenticated
from chatBot.paths import PROJECT_ROOT_PATH

ui_router = APIRouter(prefix="/v1", dependencies=[Depends(authenticated)])

favicon_router = APIRouter()


@favicon_router.get("/favicon.ico")
async def favicon():
    favicon_path = "chatBot/server/ui/favicon.ico"
    return FileResponse(favicon_path)


def format_date(value, format="%Y-%m-%d %H:%M:%S"):
    if isinstance(value, str):
        return datetime.strptime(value, format).strftime(format)
    return value


templates = Jinja2Templates(directory="chatBot/server/ui/templates")
templates.env.filters["date"] = format_date


def get_db():
    conn = sqlite3.connect(PROJECT_ROOT_PATH / "DB" / "Database.sqlite")
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
    return templates.TemplateResponse(
        "user_data.html", {"request": request, "data": data}
    )


@ui_router.post("/data/markasQ")
async def mark_as_question(request: Request):
    data = await request.json()
    id = data.get("id")
    is_question = data.get("is_question")
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE CHATHISTORY SET is_question=? WHERE id=?", (is_question, id))
    conn.commit()

    print(f"{id} - {is_question}")

    return f"{id} is marked as {is_question}"
