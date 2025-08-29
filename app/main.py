#app/main.py
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes.ping import router as ping_router
from app.routes.generate import ui_router, api_router

# 1) Налаштовуємо логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# 2) Ініціалізуємо FastAPI
app = FastAPI()

# 3) CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# 4) Статичні файли
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# 5) Підключаємо роутери
app.include_router(ping_router)    # /ping
app.include_router(ui_router)      # / & /generate (HTML)
app.include_router(api_router)     # /api/generate (JSON)