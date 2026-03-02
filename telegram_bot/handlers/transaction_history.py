from datetime import datetime
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.transactions import TransactionService
from services.categories import CategoryService
from states.states import EditStates, FilterCategoryStates, FilterPeriodStates

router = Router()
tx_service = TransactionService()
cat_service = CategoryService()

PAGE_SIZE = 4

def validate_date(date_text):
    """
    Validates if the provided text matches the DD.MM.YYYY format.

    Args:
        date_text (str): The date string to validate.

    Returns:
        str: The date in YYYY-MM-DD format if valid, None otherwise.
    """
    try:
        dt = datetime.strptime(date_text, "%d.%m.%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None

async def safe_delete_message(bot, chat_id, message_id):
    """
    Safely attempts to delete a message, ignoring errors if the message doesn't exist.

    Args:
        bot: The bot instance.
        chat_id (int): The ID of the chat.
        message_id (int): The ID of the message to delete.
    """
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception:
        pass

async def show_transactions(message: types.Message, state: FSMContext, page: int = 1, category_id: int = None, start_date: str = None, end_date: str = None):
    """
    Fetches and displays a paginated list of transactions based on filters.

    Args:
        message (types.Message): The message object to reply to.
        state (FSMContext): The FSM context for state management.
        page (int): The current page number. Defaults to 1.
        category_id (int, optional): Filter by category ID. Defaults to None.
        start_date (str, optional): Filter by start date (YYYY-MM-DD). Defaults to None.
        end_date (str, optional): Filter by end date (YYYY-MM-DD). Defaults to None.
    """
    data = await state.get_data()
    token = data.get("access_token")
    old_message_ids = data.get("history_message_ids", [])
    
    # Check state for filters if not provided
    if category_id is None:
        category_id = data.get("filter_category_id")
    else:
        await state.update_data(filter_category_id=category_id)
        
    if start_date is None:
        start_date = data.get("filter_start_date")
    else:
        await state.update_data(filter_start_date=start_date)
        
    if end_date is None:
        end_date = data.get("filter_end_date")
    else:
        await state.update_data(filter_end_date=end_date)
    
    # 1. Cleanup old messages
    for msg_id in old_message_ids:
        await safe_delete_message(message.bot, message.chat.id, msg_id)
    
    # 2. Fetch data
    response = tx_service.get_transactions(token, page=page, page_size=PAGE_SIZE, category_id=category_id, start_date=start_date, end_date=end_date)
    
    new_message_ids = []

    if not response or 'results' not in response:
        sent = await message.answer("❌ Failed to fetch transactions.")
        new_message_ids.append(sent.message_id)
        await state.update_data(history_message_ids=new_message_ids)
        return

    transactions = response['results']
    count = response['count']
    total_pages = (count + PAGE_SIZE - 1) // PAGE_SIZE

    if not transactions:
        sent = await message.answer("📭 No transactions found.")
        new_message_ids.append(sent.message_id)
        await state.update_data(history_message_ids=new_message_ids)
        return

    # 3. Send transaction cards
    for t in transactions:
        category = t.get('category', {}).get('name', 'Unknown')
        amount = t.get('amount_original', 0)
        desc = t.get('description') or t.get('raw_text') or ""
        date = t.get('date', '')[5:10] # Show MM-DD
        
        # Compact single-line format
        card_text = f"📅 {date} | 📂 {category} | 💰 **{amount}**"
        if desc:
            card_text += f" | 📝 {desc}"
        
        card_markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️", callback_data=f"trans_edit:{t['id']}"),
                InlineKeyboardButton(text="🗑️", callback_data=f"trans_del:{t['id']}")
            ]
        ])
        
        sent = await message.answer(card_text, reply_markup=card_markup, parse_mode="Markdown")
        new_message_ids.append(sent.message_id)

    # 4. Send Navigation Bar
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"trans_page:{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(text=f"Page {page}/{total_pages}", callback_data="noop"))
    
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"trans_page:{page+1}"))
    
    nav_markup = InlineKeyboardMarkup(inline_keyboard=[nav_buttons])
    sent_nav = await message.answer("Navigate:", reply_markup=nav_markup)
    new_message_ids.append(sent_nav.message_id)

    # 5. Save IDs
    await state.update_data(history_message_ids=new_message_ids)

@router.message(F.text == "🕒 Последние")
async def menu_last_transactions(message: types.Message, state: FSMContext):
    """Shows the most recent transactions, clearing all filters."""
    # Clear all filters
    await state.update_data(filter_category_id=None, filter_start_date=None, filter_end_date=None)
    await show_transactions(message, state, page=1, category_id=None, start_date=None, end_date=None)

@router.message(F.text == "📅 За период")
async def menu_transactions_period(message: types.Message, state: FSMContext):
    """Initiates filtering transactions by a specific period."""
    await state.set_state(FilterPeriodStates.waiting_for_start_date)
    await message.answer("Введите дату начала периода (ДД.ММ.ГГГГ):")

@router.message(FilterPeriodStates.waiting_for_start_date)
async def on_filter_period_start(message: types.Message, state: FSMContext):
    """Processes the start date for period filtering."""
    date_str = validate_date(message.text)
    if not date_str:
        await message.answer("❌ Неверный формат даты. Пожалуйста, используйте ДД.ММ.ГГГГ")
        return
        
    await state.update_data(temp_start_date=date_str)
    await state.set_state(FilterPeriodStates.waiting_for_end_date)
    await message.answer("Введите дату конца периода (ДД.ММ.ГГГГ):")

@router.message(FilterPeriodStates.waiting_for_end_date)
async def on_filter_period_end(message: types.Message, state: FSMContext):
    """Processes the end date for period filtering and displays the results."""
    date_str = validate_date(message.text)
    if not date_str:
        await message.answer("❌ Неверный формат даты. Пожалуйста, используйте ДД.ММ.ГГГГ")
        return
    
    data = await state.get_data()
    start_date = data.get("temp_start_date")
    
    await state.set_state(None)
    await state.update_data(filter_category_id=None) 
    await show_transactions(message, state, page=1, start_date=start_date, end_date=date_str, category_id=None)

@router.message(F.text == "📂 По категориям")
async def menu_transactions_categories(message: types.Message, state: FSMContext):
    """Initiates filtering transactions by category."""
    # Clear date filters when switching to category mode
    await state.update_data(filter_start_date=None, filter_end_date=None)
    
    data = await state.get_data()
    token = data.get("access_token")
    categories_response = cat_service.get_categories(token, page_size=100)
    
    if not categories_response or 'results' not in categories_response:
        await message.answer("Не удалось загрузить категории")
        return
        
    categories = categories_response['results']
    
    buttons = []
    row = []
    for cat in categories:
        row.append(InlineKeyboardButton(text=cat['name'], callback_data=f"filter_cat:{cat['id']}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
        
    buttons.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="filter_cat:cancel")])
    
    await state.set_state(FilterCategoryStates.selecting_category)
    await message.answer("Выберите категорию для фильтрации:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(FilterCategoryStates.selecting_category, F.data.startswith("filter_cat:"))
async def on_filter_category_select(callback: types.CallbackQuery, state: FSMContext):
    """Processes the selected category for filtering and displays the results."""
    cat_id_str = callback.data.split(":")[1]
    
    if cat_id_str == "cancel":
        await state.set_state(None)
        await callback.message.delete()
        await callback.answer("Отменено")
        return
        
    cat_id = int(cat_id_str)
    
    await callback.message.delete()
    await callback.answer()
    
    await state.set_state(None) # Reset state so we are not stuck in selecting_category
    await show_transactions(callback.message, state, page=1, category_id=cat_id)

@router.callback_query(F.data.startswith("trans_page:"))
async def on_page_change(callback: types.CallbackQuery, state: FSMContext):
    """Handles pagination for the transaction list."""
    page = int(callback.data.split(":")[1])
    await show_transactions(callback.message, state, page=page)
    await callback.answer()

@router.callback_query(F.data.startswith("trans_del:"))
async def on_delete_transaction(callback: types.CallbackQuery, state: FSMContext):
    """Deletes a transaction upon user request."""
    trans_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    token = data.get("access_token")
    
    success = tx_service.delete_transaction(token, trans_id)
    
    if success:
        await callback.answer("✅ Deleted")
        # Refresh current view (page 1 for simplicity, or we could track current page in state)
        await show_transactions(callback.message, state, page=1)
    else:
        await callback.answer("❌ Failed to delete")

@router.callback_query(F.data.startswith("trans_edit:"))
async def on_edit_transaction(callback: types.CallbackQuery, state: FSMContext):
    """Initiates the process to edit a transaction."""
    trans_id = int(callback.data.split(":")[1])
    await state.update_data(editing_trans_id=trans_id)
    await state.set_state(EditStates.selecting_field)
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 Сумма", callback_data="edit_select:amount"),
            InlineKeyboardButton(text="📂 Категория", callback_data="edit_select:category")
        ],
        [
            InlineKeyboardButton(text="📝 Описание", callback_data="edit_select:desc")
        ],
        [
            InlineKeyboardButton(text="🔙 Отмена", callback_data="edit_select:cancel")
        ]
    ])
    
    await callback.message.answer("Что вы хотите изменить?", reply_markup=markup)
    await callback.answer()

@router.callback_query(EditStates.selecting_field, F.data.startswith("edit_select:"))
async def on_select_edit_field(callback: types.CallbackQuery, state: FSMContext):
    """Processes the selection of the field to be edited."""
    action = callback.data.split(":")[1]
    
    if action == "cancel":
        await state.set_state(None)
        await callback.message.delete()
        await callback.answer("Отменено")
        return

    if action == "amount":
        await state.set_state(EditStates.waiting_for_amount)
        await callback.message.answer("Введите новую сумму:")
        await callback.message.delete()
    
    elif action == "desc":
        await state.set_state(EditStates.waiting_for_description)
        await callback.message.answer("Введите новое описание:")
        await callback.message.delete()
        
    elif action == "category":
        data = await state.get_data()
        token = data.get("access_token")
        categories_response = cat_service.get_categories(token, page_size=100)
        
        if not categories_response or 'results' not in categories_response:
            await callback.answer("Не удалось загрузить категории")
            return
        
        categories = categories_response['results']
            
        buttons = []
        row = []
        for cat in categories:
            row.append(InlineKeyboardButton(text=cat['name'], callback_data=f"edit_cat:{cat['id']}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
            
        buttons.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="edit_cat:cancel")])
        
        await state.set_state(EditStates.waiting_for_category)
        await callback.message.answer("Выберите категорию:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
        await callback.message.delete()
    
    await callback.answer()

@router.message(EditStates.waiting_for_amount)
async def on_edit_amount_input(message: types.Message, state: FSMContext):
    """Processes the new amount input and updates the transaction."""
    try:
        amount = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")
        return
        
    data = await state.get_data()
    trans_id = data.get("editing_trans_id")
    token = data.get("access_token")
    
    success = tx_service.update_transaction(token, trans_id, {"amount": amount})
    
    if success:
        await message.answer("✅ Сумма обновлена!")
        await state.set_state(None)
        await show_transactions(message, state, page=1)
    else:
        await message.answer("❌ Ошибка при обновлении.")
        await state.set_state(None)

@router.message(EditStates.waiting_for_description)
async def on_edit_desc_input(message: types.Message, state: FSMContext):
    """Processes the new description input and updates the transaction."""
    desc = message.text
    data = await state.get_data()
    trans_id = data.get("editing_trans_id")
    token = data.get("access_token")
    
    success = tx_service.update_transaction(token, trans_id, {"description": desc})
    
    if success:
        await message.answer("✅ Описание обновлено!")
        await state.set_state(None)
        await show_transactions(message, state, page=1)
    else:
        await message.answer("❌ Ошибка при обновлении.")
        await state.set_state(None)

@router.callback_query(EditStates.waiting_for_category, F.data.startswith("edit_cat:"))
async def on_edit_category_select(callback: types.CallbackQuery, state: FSMContext):
    """Processes the new category selection and updates the transaction."""
    cat_id_str = callback.data.split(":")[1]
    
    if cat_id_str == "cancel":
        await state.set_state(None)
        await callback.message.delete()
        await callback.answer("Отменено")
        return
        
    cat_id = int(cat_id_str)
    data = await state.get_data()
    trans_id = data.get("editing_trans_id")
    token = data.get("access_token")
    
    success = tx_service.update_transaction(token, trans_id, {"category_id": cat_id})
    
    if success:
        await callback.message.delete()
        await callback.message.answer("✅ Категория обновлена!")
        await state.set_state(None)
        # We need 'message' object to refresh history. Callback has it.
        await show_transactions(callback.message, state, page=1)
    else:
        await callback.message.answer("❌ Ошибка при обновлении.")
        await state.set_state(None)
    
    await callback.answer()

@router.callback_query(F.data == "noop")
async def on_noop(callback: types.CallbackQuery):
    """No-op handler for non-functional inline buttons."""
    await callback.answer()