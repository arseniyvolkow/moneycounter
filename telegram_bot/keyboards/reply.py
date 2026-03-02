from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from config import API_BASE_URL, WEBAPP_URL

# Main menu for the bot after successful login
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💱 Транзакции"), KeyboardButton(text="📊 Аналитика")],
        [KeyboardButton(text="💰 Счета"), KeyboardButton(text="📱 Куплю ли я?")],
        [KeyboardButton(text="⚙️ Настройки")]
    ],
    resize_keyboard=True,
    persistent=True
)

# Sub-menu for transaction options
transactions_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🕒 Последние"), KeyboardButton(text="📅 За период")],
        [KeyboardButton(text="📂 По категориям"), KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True,
    persistent=True
)

# Sub-menu for account options
accounts_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить новый счет"), KeyboardButton(text="💸 Переводы между счетами")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True,
    persistent=True
)

# Sub-menu for settings options
settings_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💱 Изменить валюту"), KeyboardButton(text="📂 Изменить категории")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True,
    persistent=True
)

# Sub-menu for category management
categories_settings_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить категорию")],
        [KeyboardButton(text="🔙 К настройкам")]
    ],
    resize_keyboard=True,
    persistent=True
)

# Sub-menu for analytics reports
analytics_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 За неделю"), KeyboardButton(text="📅 За месяц")],
        [KeyboardButton(text="📉 Сравнение"), KeyboardButton(text="📥 PDF-отчет")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True,
    persistent=True
)

# Login menu linking to the WebApp
login_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Register", web_app=WebAppInfo(url=f"{WEBAPP_URL}/api/auth/webapp/register/"))],
        [KeyboardButton(text="🔑 Login", web_app=WebAppInfo(url=f"{WEBAPP_URL}/api/auth/webapp/login/"))]
    ],
    resize_keyboard=True
)