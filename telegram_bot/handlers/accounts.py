from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.accounts import AccountService
from states.states import AddAccountStates, EditAccountStates, TransferStates
from keyboards.reply import accounts_menu

router = Router()
acc_service = AccountService()

PAGE_SIZE = 5

async def safe_delete_message(bot, chat_id, message_id):
    """Safely delete a message by ID without raising an error if it fails."""
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception:
        pass

async def show_accounts(message: types.Message, state: FSMContext, page: int = 1):
    """
    Displays a paginated list of accounts.
    
    Args:
        message (types.Message): The message object.
        state (FSMContext): The FSM context containing the user's token.
        page (int): The current page number.
    """
    data = await state.get_data()
    token = data.get("access_token")
    old_message_ids = data.get("account_message_ids", [])
    
    # 1. Cleanup old messages
    for msg_id in old_message_ids:
        await safe_delete_message(message.bot, message.chat.id, msg_id)
    
    # 2. Fetch data
    response = acc_service.get_accounts(token, page=page, page_size=PAGE_SIZE)
    
    new_message_ids = []

    if not response or 'results' not in response:
        sent = await message.answer("❌ Failed to fetch accounts.")
        new_message_ids.append(sent.message_id)
        await state.update_data(account_message_ids=new_message_ids)
        return

    accounts = response['results']
    count = response['count']
    total_pages = (count + PAGE_SIZE - 1) // PAGE_SIZE

    if not accounts:
        sent = await message.answer("📭 No accounts found.")
        new_message_ids.append(sent.message_id)
        await state.update_data(account_message_ids=new_message_ids)
        return

    # 3. Send account cards
    for acc in accounts:
        name = acc.get('name', 'Unknown')
        balance = acc.get('balance', 0)
        currency = acc.get('currency', '')
        # If currency is an object/dict
        currency_code = currency
        if isinstance(currency, dict):
            currency_code = currency.get('code', '')
        
        card_text = f"🔹 **{name}**\n💰 Balance: {balance} {currency_code}"
        
        card_markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Edit", callback_data=f"acc_edit:{acc['id']}")
            ]
        ])
        
        sent = await message.answer(card_text, reply_markup=card_markup, parse_mode="Markdown")
        new_message_ids.append(sent.message_id)

    # 4. Send Navigation Bar
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"acc_page:{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(text=f"Page {page}/{total_pages}", callback_data="noop"))
    
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"acc_page:{page+1}"))
    
    nav_markup = InlineKeyboardMarkup(inline_keyboard=[nav_buttons])
    sent_nav = await message.answer("Navigate:", reply_markup=nav_markup)
    new_message_ids.append(sent_nav.message_id)

    # 5. Save IDs
    await state.update_data(account_message_ids=new_message_ids)

async def cmd_accounts(message: types.Message, state: FSMContext):
    """Handles the 'Accounts' menu button."""
    data = await state.get_data()
    token = data.get("access_token")
    
    if not token:
        await message.answer("Please login first.")
        return

    # Send Reply Menu
    await message.answer("🏦 **Управление счетами**", reply_markup=accounts_menu, parse_mode="Markdown")
    
    # Show the list
    await show_accounts(message, state, page=1)

@router.callback_query(F.data.startswith("acc_page:"))
async def on_account_page(callback: types.CallbackQuery, state: FSMContext):
    """Handles pagination for accounts list."""
    page = int(callback.data.split(":")[1])
    await show_accounts(callback.message, state, page=page)
    await callback.answer()

# --- ADD ACCOUNT ---
@router.message(F.text == "➕ Добавить новый счет")
async def on_account_add(message: types.Message, state: FSMContext):
    """Starts the process of adding a new account."""
    await state.set_state(AddAccountStates.waiting_for_name)
    await message.answer("Enter account name:")

@router.message(AddAccountStates.waiting_for_name)
async def add_acc_name(message: types.Message, state: FSMContext):
    """Captures the new account's name and prompts for currency."""
    await state.update_data(new_acc_name=message.text)
    
    data = await state.get_data()
    token = data.get("access_token")
    currencies = acc_service.get_currencies(token)
    
    if not currencies:
        await message.answer("Failed to load currencies.")
        await state.set_state(None)
        return

    buttons = []
    row = []
    for cur in currencies:
        # Currency might be serialized object
        code = cur.get('code')
        cid = cur.get('id')
        row.append(InlineKeyboardButton(text=code, callback_data=f"add_acc_cur:{cid}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="Cancel", callback_data="add_acc_cancel")])
    
    await state.set_state(AddAccountStates.waiting_for_currency)
    await message.answer("Select currency:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(AddAccountStates.waiting_for_currency, F.data.startswith("add_acc_cur:"))
async def add_acc_currency(callback: types.CallbackQuery, state: FSMContext):
    """Captures the new account's currency and prompts for balance."""
    cur_id = int(callback.data.split(":")[1])
    await state.update_data(new_acc_cur=cur_id)
    await state.set_state(AddAccountStates.waiting_for_balance)
    await callback.message.answer("Enter initial balance:")
    await callback.answer()

@router.callback_query(AddAccountStates.waiting_for_currency, F.data == "add_acc_cancel")
async def add_acc_cancel(callback: types.CallbackQuery, state: FSMContext):
    """Cancels the account creation process."""
    await state.set_state(None)
    await callback.message.answer("Cancelled.")
    await callback.answer()

@router.message(AddAccountStates.waiting_for_balance)
async def add_acc_balance(message: types.Message, state: FSMContext):
    """Captures the new account's initial balance and creates the account."""
    try:
        balance = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("Invalid number. Try again.")
        return

    data = await state.get_data()
    token = data.get("access_token")
    name = data.get("new_acc_name")
    cur_id = data.get("new_acc_cur")
    
    success = acc_service.create_account(token, name, cur_id, balance)
    
    if success:
        await message.answer("✅ Account created!")
        await state.set_state(None)
        await show_accounts(message, state, page=1)
    else:
        await message.answer("❌ Failed to create account.")
        await state.set_state(None)

# --- EDIT ACCOUNT ---
@router.callback_query(F.data.startswith("acc_edit:"))
async def on_account_edit(callback: types.CallbackQuery, state: FSMContext):
    """Initiates editing an account."""
    acc_id = int(callback.data.split(":")[1])
    await state.update_data(edit_acc_id=acc_id)
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Name", callback_data="edit_acc_op:name"),
            InlineKeyboardButton(text="💰 Balance", callback_data="edit_acc_op:balance")
        ],
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="edit_acc_op:cancel")]
    ])
    
    await state.set_state(EditAccountStates.selecting_field)
    await callback.message.answer("What do you want to edit?", reply_markup=markup)
    await callback.answer()

@router.callback_query(EditAccountStates.selecting_field, F.data.startswith("edit_acc_op:"))
async def on_edit_acc_op(callback: types.CallbackQuery, state: FSMContext):
    """Processes the field selection to edit."""
    op = callback.data.split(":")[1]
    
    if op == "cancel":
        await state.set_state(None)
        await callback.message.delete()
        await callback.answer("Cancelled")
        return
    
    if op == "name":
        await state.set_state(EditAccountStates.waiting_for_name)
        await callback.message.answer("Enter new name:")
    elif op == "balance":
        await state.set_state(EditAccountStates.waiting_for_balance)
        await callback.message.answer("Enter new balance:")
    
    await callback.answer()

@router.message(EditAccountStates.waiting_for_name)
async def edit_acc_name(message: types.Message, state: FSMContext):
    """Updates the account's name."""
    new_name = message.text
    data = await state.get_data()
    token = data.get("access_token")
    acc_id = data.get("edit_acc_id")
    
    if acc_service.update_account(token, acc_id, {"name": new_name}):
        await message.answer("✅ Name updated!")
        await state.set_state(None)
        await show_accounts(message, state, page=1)
    else:
        await message.answer("❌ Failed to update.")
        await state.set_state(None)

@router.message(EditAccountStates.waiting_for_balance)
async def edit_acc_balance(message: types.Message, state: FSMContext):
    """Updates the account's balance."""
    try:
        new_balance = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("Invalid number.")
        return
        
    data = await state.get_data()
    token = data.get("access_token")
    acc_id = data.get("edit_acc_id")
    
    if acc_service.update_account(token, acc_id, {"balance": new_balance}):
        await message.answer("✅ Balance updated!")
        await state.set_state(None)
        await show_accounts(message, state, page=1)
    else:
        await message.answer("❌ Failed to update.")
        await state.set_state(None)

# --- TRANSFER ---
@router.message(F.text == "💸 Переводы между счетами")
async def on_account_transfer(message: types.Message, state: FSMContext):
    """Initiates a money transfer between accounts."""
    data = await state.get_data()
    token = data.get("access_token")
    
    # Fetch all accounts (might need pagination if user has many, but assume < 20 for now)
    # Reuse get_accounts with large page size
    response = acc_service.get_accounts(token, page=1, page_size=100)
    if not response or not response.get('results'):
        await message.answer("No accounts found!")
        return
    
    accounts = response['results']
    await state.update_data(transfer_accounts=accounts)
    
    buttons = []
    for acc in accounts:
        buttons.append([InlineKeyboardButton(text=f"{acc['name']} ({acc['balance']})", callback_data=f"trans_src:{acc['id']}")])
    buttons.append([InlineKeyboardButton(text="Cancel", callback_data="trans_cancel")])
    
    await state.set_state(TransferStates.selecting_source)
    await message.answer("Select Source Account:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(TransferStates.selecting_source, F.data.startswith("trans_src:"))
async def on_transfer_source(callback: types.CallbackQuery, state: FSMContext):
    """Selects the source account for the transfer."""
    src_id = int(callback.data.split(":")[1])
    await state.update_data(transfer_src_id=src_id)
    
    data = await state.get_data()
    accounts = data.get("transfer_accounts", [])
    
    buttons = []
    for acc in accounts:
        if acc['id'] != src_id:
            buttons.append([InlineKeyboardButton(text=f"{acc['name']} ({acc['balance']})", callback_data=f"trans_dst:{acc['id']}")])
    buttons.append([InlineKeyboardButton(text="Cancel", callback_data="trans_cancel")])
    
    await state.set_state(TransferStates.selecting_destination)
    await callback.message.answer("Select Destination Account:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@router.callback_query(TransferStates.selecting_destination, F.data.startswith("trans_dst:"))
async def on_transfer_dest(callback: types.CallbackQuery, state: FSMContext):
    """Selects the destination account for the transfer."""
    dst_id = int(callback.data.split(":")[1])
    await state.update_data(transfer_dst_id=dst_id)
    
    await state.set_state(TransferStates.waiting_for_amount)
    await callback.message.answer("Enter amount to transfer:")
    await callback.answer()

@router.callback_query(F.data == "trans_cancel")
async def on_transfer_cancel(callback: types.CallbackQuery, state: FSMContext):
    """Cancels the transfer process."""
    await state.set_state(None)
    await callback.message.answer("Transfer cancelled.")
    await callback.answer()

@router.message(TransferStates.waiting_for_amount)
async def on_transfer_amount(message: types.Message, state: FSMContext):
    """Executes the transfer of funds between accounts."""
    try:
        amount = float(message.text.replace(',', '.'))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Invalid amount. Must be positive.")
        return
        
    data = await state.get_data()
    token = data.get("access_token")
    src_id = data.get("transfer_src_id")
    dst_id = data.get("transfer_dst_id")
    
    # Fetch current balances to be safe
    src_acc = acc_service.get_account(token, src_id)
    dst_acc = acc_service.get_account(token, dst_id)
    
    if not src_acc or not dst_acc:
        await message.answer("❌ Error fetching account details.")
        await state.set_state(None)
        return
        
    src_bal = float(src_acc['balance'])
    dst_bal = float(dst_acc['balance'])
    
    if src_bal < amount:
        await message.answer(f"❌ Insufficient funds. Source balance: {src_bal}")
        # Could stay in state to let them retry amount, but for now reset
        return

    # Execute
    # Ideally this should be atomic transaction on backend, but here we do 2 calls.
    # We update source first.
    if acc_service.update_account(token, src_id, {"balance": src_bal - amount}):
        if acc_service.update_account(token, dst_id, {"balance": dst_bal + amount}):
            await message.answer("✅ Transfer successful!")
            await show_accounts(message, state, page=1)
        else:
            # Critical error: Source deducted, Dest not added.
            # Try to rollback source
            acc_service.update_account(token, src_id, {"balance": src_bal}) # Revert
            await message.answer("❌ Transfer failed (rolled back).")
    else:
        await message.answer("❌ Transfer failed.")
        
    await state.set_state(None)

@router.callback_query(F.data == "noop")
async def on_noop(callback: types.CallbackQuery):
    """No-op handler."""
    await callback.answer()
