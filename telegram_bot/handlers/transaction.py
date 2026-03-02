from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ContentType
from services.accounts import AccountService
from services.transactions import TransactionService
import os

router = Router()
acc_service = AccountService()
tx_service = TransactionService()

@router.message(F.content_type == ContentType.VOICE)
async def handle_voice(message: types.Message, state: FSMContext):
    """
    Handles incoming voice messages, downloading the audio file and submitting it
    to the backend API for transcription and transaction processing.
    """
    data = await state.get_data()
    token = data.get("access_token")
    
    await message.bot.send_chat_action(message.chat.id, action="upload_voice") # "record_voice" or similar
    
    # We need a default account. For now, hardcode or pick first?
    # Ideally prompt user. But for speed:
    response = acc_service.get_accounts(token)
    if not response or 'results' not in response:
        await message.answer("❌ Failed to fetch accounts.")
        return
        
    accounts = response['results']
    if not accounts:
        await message.answer("❌ No accounts found. Please create one in the app first.")
        return
    
    default_account_id = accounts[0]['id'] # Pick first account

    file_id = message.voice.file_id
    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    
    # Download file
    # Ensure tmp dir exists
    os.makedirs("tmp", exist_ok=True)
    local_filename = f"tmp/{file_id}.ogg"
    await message.bot.download_file(file_path, local_filename)
    
    try:
        with open(local_filename, "rb") as f:
             # Pass chat_id so worker can reply
             success = tx_service.create_voice_transaction(token, f, default_account_id, chat_id=message.chat.id)
        
        if success:
             await message.answer(f"✅ Voice received! Processing transaction for Account #{default_account_id}...")
        else:
             await message.answer("❌ Failed to send voice to API.")
    finally:
        if os.path.exists(local_filename):
            os.remove(local_filename)

@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: types.Message, state: FSMContext):
    """
    Handles plain text messages (non-commands and non-menu items), submitting them
    to the backend API for AI-based transaction parsing.
    """
    data = await state.get_data()
    token = data.get("access_token")

    # Ignore menu commands if they leaked here (handled by menu.py usually if router order is correct)
    if message.text in [
        "💱 Транзакции", 
        "🕒 Последние", 
        "📅 За период", 
        "📂 По категориям", 
        "🔙 Назад",
        "📊 Аналитика", 
        "💰 Счета", 
        "📱 Куплю ли я?", 
        "⚙️ Настройки"
    ]:
        return

    await message.bot.send_chat_action(message.chat.id, action="typing")

    response = acc_service.get_accounts(token)
    if not response or 'results' not in response:
        await message.answer("❌ Failed to fetch accounts.")
        return

    accounts = response['results']
    if not accounts:
        await message.answer("❌ No accounts found.")
        return
    default_account_id = accounts[0]['id']

    # Pass chat_id so worker can reply
    success = tx_service.create_text_transaction(token, message.text, default_account_id, chat_id=message.chat.id)
    
    if success:
        await message.answer(f"✅ Text received! Processing transaction for Account #{default_account_id}...")
    else:
        await message.answer("❌ Failed to send transaction to API.")