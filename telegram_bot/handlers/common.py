import json
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.states import LoginStates
from services.auth import AuthService
from keyboards.reply import main_menu, login_menu

router = Router()
auth_service = AuthService()

WELCOME_MESSAGE = (
    "✅ <b>Login successful! Welcome back, {username}!</b>\n\n"
    "I'm here to help you track your finances effortlessly. Here's how you can use me:\n\n"
    "📝 <b>Add Transactions via Text</b>\n"
    "Just type what you spent, e.g., 'Coffee 150' or 'Dinner 1200'. I'll automatically categorize it for you!\n\n"
    "🎙️ <b>Add Transactions via Voice</b>\n"
    "Send me a voice message like 'Spent 500 on groceries' and I'll process it immediately.\n\n"
    "📊 <b>Manage Your Money</b>\n"
    "Use the menu below to:\n"
    "• 💱 <b>Транзакции</b> - View and filter your history\n"
    "• 💰 <b>Счета</b> - Check your balances\n"
    "• 📊 <b>Аналитика</b> - See where your money goes\n\n"
    "Simply send me a message or record a voice note to start!"
)

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Handles the /start command, displaying the welcome message and login menu."""
    await message.answer(
        "👋 Welcome to MoneyCounter Bot!\n"
        "Please login or register using the buttons below to start tracking your finances.",
        reply_markup=login_menu
    )

@router.message(Command("help"))
async def cmd_help(message: types.Message, state: FSMContext):
    """Handles the /help command, displaying instructions to the user."""
    data = await state.get_data()
    username = data.get("username", "User")
    await message.answer(
        WELCOME_MESSAGE.format(username=username),
        parse_mode="HTML"
    )

@router.message(F.web_app_data)
async def process_web_app_data(message: types.Message, state: FSMContext):
    """Processes authentication data received from the Telegram Mini App."""
    try:
        data = json.loads(message.web_app_data.data)
        
        # Check if it's a login success message
        if data.get("access") and data.get("refresh"):
            username = data.get('username', 'User')
            await state.update_data(
                access_token=data["access"], 
                refresh_token=data["refresh"],
                username=username
            )
            await message.answer(
                WELCOME_MESSAGE.format(username=username), 
                reply_markup=main_menu,
                parse_mode="HTML"
            )
            await state.set_state(None) # Clear state
        else:
            await message.answer("❌ Received invalid data from Web App.", reply_markup=login_menu)
            
    except json.JSONDecodeError:
        await message.answer("❌ Failed to process Web App data.", reply_markup=login_menu)
    except Exception as e:
        print(f"Web App Error: {e}")
        await message.answer("❌ An error occurred during login.", reply_markup=login_menu)

# Keeping the old /login command for fallback/legacy support if needed, 
# or you can remove it if you want to enforce Web App login only.
@router.message(Command("login"))
async def cmd_login(message: types.Message, state: FSMContext):
    """Starts the legacy login process by asking for the username."""
    await message.answer("Please enter your username:")
    await state.set_state(LoginStates.waiting_for_username)

@router.message(LoginStates.waiting_for_username)
async def process_username(message: types.Message, state: FSMContext):
    """Processes the username input and asks for the password."""
    await state.update_data(username=message.text.strip())
    await message.answer("Please enter your password:")
    await state.set_state(LoginStates.waiting_for_password)

@router.message(LoginStates.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    """Processes the password input, authenticates the user, and transitions to the main menu."""
    data = await state.get_data()
    username = data.get("username")
    password = message.text.strip()

    # Clear password from chat history (optional/best practice, but hard in simple bot)
    # await message.delete() 

    tokens = auth_service.login(username, password)
    if tokens:
        await state.update_data(access_token=tokens["access"], refresh_token=tokens["refresh"])
        await message.answer(
            WELCOME_MESSAGE.format(username=username), 
            reply_markup=main_menu,
            parse_mode="HTML"
        )
        await state.set_state(None) # Clear state
    else:
        await message.answer("❌ Login failed. Please try /login again.", reply_markup=login_menu)
        await state.clear()