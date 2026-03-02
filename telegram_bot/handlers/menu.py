from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_analytics_keyboard
from keyboards.reply import main_menu, transactions_menu, settings_menu, analytics_menu
from handlers.accounts import cmd_accounts

router = Router()

@router.message(F.text == "💱 Транзакции")
async def menu_transactions(message: types.Message):
    """Displays the transactions sub-menu."""
    await message.answer("Выберите действие:", reply_markup=transactions_menu)

@router.message(F.text == "🔙 Назад")
async def menu_back(message: types.Message):
    """Navigates back to the main menu."""
    await message.answer("Главное меню", reply_markup=main_menu)

@router.message(F.text == "📊 Аналитика")
async def menu_analytics(message: types.Message):
    """Displays the analytics sub-menu."""
    await message.answer("Выберите отчет:", reply_markup=analytics_menu)

@router.message(F.text == "💰 Счета")
async def menu_accounts(message: types.Message, state: FSMContext):
    """Delegates to the accounts handler to display user accounts."""
    # Delegate to accounts handler logic
    await cmd_accounts(message, state)

@router.message(F.text == "📱 Куплю ли я?")
async def menu_goals(message: types.Message):
    """Placeholder handler for the upcoming AI Advice feature."""
    await message.answer("🚧 AI Advice feature is coming soon!")

@router.message(F.text == "⚙️ Настройки")
async def menu_settings(message: types.Message):
    """Displays the settings sub-menu."""
    await message.answer("⚙️ Настройки:", reply_markup=settings_menu)

# Callback handlers for analytics
@router.callback_query(F.data.startswith("analytics_"))
async def analytics_callback(callback: types.CallbackQuery):
    """Handles callback queries from analytics inline keyboards."""
    await callback.answer("Construction work in progress! 🚧")
    # await callback.message.answer("Feature coming soon.")