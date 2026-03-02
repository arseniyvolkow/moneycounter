from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_confirm_keyboard():
    """
    Returns an inline keyboard for confirming or editing a transaction.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_transaction"),
                InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_transaction")
            ],
            [
                InlineKeyboardButton(text="🗑 Удалить", callback_data="delete_transaction")
            ]
        ]
    )

def get_analytics_keyboard():
    """
    Returns an inline keyboard for analytics options.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 За неделю", callback_data="analytics_week"),
                InlineKeyboardButton(text="📅 За месяц", callback_data="analytics_month")
            ],
            [
                InlineKeyboardButton(text="📉 Сравнить с прошлым месяцем", callback_data="analytics_compare")
            ],
             [
                InlineKeyboardButton(text="📥 Скачать PDF-отчет", callback_data="analytics_pdf")
            ]
        ]
    )