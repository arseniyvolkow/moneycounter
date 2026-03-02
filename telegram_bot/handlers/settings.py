from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.auth import AuthService
from services.accounts import AccountService
from services.categories import CategoryService
from states.states import SettingsStates, CategorySettingsStates
from keyboards.reply import categories_settings_menu, settings_menu

router = Router()
auth_service = AuthService()
acc_service = AccountService()
cat_service = CategoryService()

PAGE_SIZE = 4

async def safe_delete_message(bot, chat_id, message_id):
    """Safely delete a message by ID without raising an error if it fails."""
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception:
        pass

async def show_categories(message: types.Message, state: FSMContext, page: int = 1):
    """
    Displays a paginated list of categories for the user to manage. 
    
    Args:
        message (types.Message): The message object.
        state (FSMContext): The FSM context containing the user's token.
        page (int): The current page number.
    """
    data = await state.get_data()
    token = data.get("access_token")
    old_message_ids = data.get("cat_message_ids", [])
    
    # 1. Cleanup old messages
    for msg_id in old_message_ids:
        await safe_delete_message(message.bot, message.chat.id, msg_id)
    
    # 2. Fetch data
    response = cat_service.get_categories(token, page=page, page_size=PAGE_SIZE)
    
    new_message_ids = []

    if not response or 'results' not in response:
        sent = await message.answer("❌ Failed to fetch categories.")
        new_message_ids.append(sent.message_id)
        await state.update_data(cat_message_ids=new_message_ids)
        return

    categories = response['results']
    count = response['count']
    total_pages = (count + PAGE_SIZE - 1) // PAGE_SIZE

    if not categories:
        sent = await message.answer("📭 No categories found.")
        new_message_ids.append(sent.message_id)
        await state.update_data(cat_message_ids=new_message_ids)
        return

    # 3. Send category cards
    for cat in categories:
        name = cat.get('name', 'Unknown')
        ctype = cat.get('type', 'Unknown')
        is_essential = "Essential" if cat.get('is_essential') else "Optional"
        
        card_text = f"📂 **{name}**\nType: {ctype} | {is_essential}"
        
        card_markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Edit", callback_data=f"cat_edit:{cat['id']}"),
                InlineKeyboardButton(text="🗑️ Delete", callback_data=f"cat_del:{cat['id']}")
            ]
        ])
        
        sent = await message.answer(card_text, reply_markup=card_markup, parse_mode="Markdown")
        new_message_ids.append(sent.message_id)

    # 4. Send Navigation Bar
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"cat_page:{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(text=f"Page {page}/{total_pages}", callback_data="noop"))
    
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"cat_page:{page+1}"))
    
    nav_markup = InlineKeyboardMarkup(inline_keyboard=[nav_buttons])
    sent_nav = await message.answer("Navigate:", reply_markup=nav_markup)
    new_message_ids.append(sent_nav.message_id)

    # 5. Save IDs
    await state.update_data(cat_message_ids=new_message_ids)

@router.message(F.text == "💱 Изменить валюту")
async def settings_currency(message: types.Message, state: FSMContext):
    """Initiates the process to change the user's base currency."""
    data = await state.get_data()
    token = data.get("access_token")
    
    if not token:
        await message.answer("Please login first.")
        return

    # Get current profile to show current currency
    profile = auth_service.get_profile(token)
    current_currency = profile.get('base_currency') if profile else "Unknown"

    currencies = acc_service.get_currencies(token)
    if not currencies:
        await message.answer("Failed to load currencies.")
        return

    buttons = []
    row = []
    for cur in currencies:
        code = cur.get('code')
        # Mark current one
        text = f"✅ {code}" if code == current_currency else code
        row.append(InlineKeyboardButton(text=text, callback_data=f"set_cur:{code}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
        
    buttons.append([InlineKeyboardButton(text="🔙 Cancel", callback_data="set_cur:cancel")])
    
    await state.set_state(SettingsStates.selecting_currency)
    await message.answer(f"Current currency: **{current_currency}**\nSelect new currency:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="Markdown")

@router.callback_query(SettingsStates.selecting_currency, F.data.startswith("set_cur:"))
async def on_set_currency(callback: types.CallbackQuery, state: FSMContext):
    """Processes the selection of the new base currency."""
    code = callback.data.split(":")[1]
    
    if code == "cancel":
        await state.set_state(None)
        await callback.message.delete()
        await callback.answer("Cancelled")
        return
        
    data = await state.get_data()
    token = data.get("access_token")
    
    success = auth_service.update_profile(token, {"base_currency": code})
    
    if success:
        await callback.message.delete()
        await callback.message.answer(f"✅ Currency updated to {code}!")
        await state.set_state(None)
    else:
        await callback.message.answer("❌ Failed to update currency.")
        await state.set_state(None)
    
    await callback.answer()

@router.message(F.text == "📂 Изменить категории")
async def settings_categories(message: types.Message, state: FSMContext):
    """Displays the category management menu."""
    await message.answer("📂 Управление категориями", reply_markup=categories_settings_menu)
    await show_categories(message, state, page=1)

@router.message(F.text == "🔙 К настройкам")
async def categories_back(message: types.Message):
    """Navigates back to the settings menu."""
    await message.answer("⚙️ Настройки:", reply_markup=settings_menu)

@router.callback_query(F.data.startswith("cat_page:"))
async def on_cat_page(callback: types.CallbackQuery, state: FSMContext):
    """Handles category list pagination."""
    page = int(callback.data.split(":")[1])
    await show_categories(callback.message, state, page=page)
    await callback.answer()

@router.callback_query(F.data.startswith("cat_del:"))
async def on_cat_del(callback: types.CallbackQuery, state: FSMContext):
    """Deletes a category."""
    cat_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    token = data.get("access_token")
    
    if cat_service.delete_category(token, cat_id):
        await callback.answer("✅ Category deleted!")
        await show_categories(callback.message, state, page=1)
    else:
        await callback.answer("❌ Failed to delete category.")

# --- ADD CATEGORY ---
@router.message(F.text == "➕ Добавить категорию")
async def on_add_category(message: types.Message, state: FSMContext):
    """Starts the process of adding a new category."""
    await state.set_state(CategorySettingsStates.waiting_for_name)
    await message.answer("Enter category name:")

@router.message(CategorySettingsStates.waiting_for_name)
async def add_cat_name(message: types.Message, state: FSMContext):
    """Captures the new category's name."""
    await state.update_data(new_cat_name=message.text)
    
    # Ask for type
    buttons = [
        [InlineKeyboardButton(text="Income", callback_data="cat_type:INCOME")],
        [InlineKeyboardButton(text="Expense", callback_data="cat_type:EXPENSE")]
    ]
    await state.set_state(CategorySettingsStates.waiting_for_type)
    await message.answer("Select category type:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(CategorySettingsStates.waiting_for_type, F.data.startswith("cat_type:"))
async def add_cat_type(callback: types.CallbackQuery, state: FSMContext):
    """Captures the new category's type (INCOME/EXPENSE)."""
    ctype = callback.data.split(":")[1]
    await state.update_data(new_cat_type=ctype)
    
    # Ask for is_essential
    buttons = [
        [InlineKeyboardButton(text="Essential", callback_data="cat_ess:True")],
        [InlineKeyboardButton(text="Optional", callback_data="cat_ess:False")]
    ]
    await state.set_state(CategorySettingsStates.waiting_for_essential)
    await callback.message.answer("Is it essential?", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@router.callback_query(CategorySettingsStates.waiting_for_essential, F.data.startswith("cat_ess:"))
async def add_cat_essential(callback: types.CallbackQuery, state: FSMContext):
    """Captures the new category's 'essential' flag and creates it."""
    is_essential = callback.data.split(":")[1] == "True"
    
    data = await state.get_data()
    token = data.get("access_token")
    name = data.get("new_cat_name")
    ctype = data.get("new_cat_type")
    
    if cat_service.create_category(token, name, ctype, is_essential):
        await callback.message.delete()
        await callback.message.answer("✅ Category created!")
        await state.set_state(None)
        await show_categories(callback.message, state, page=1)
    else:
        await callback.message.answer("❌ Failed to create category.")
        await state.set_state(None)
    
    await callback.answer()

@router.callback_query(F.data.startswith("cat_edit:"))
async def on_cat_edit(callback: types.CallbackQuery):
    """Placeholder handler for editing a category."""
    await callback.answer("Edit category coming soon!", show_alert=True)

@router.callback_query(F.data == "noop")
async def on_noop(callback: types.CallbackQuery):
    """No-op handler."""
    await callback.answer()