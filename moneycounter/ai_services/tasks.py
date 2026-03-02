import os
import logging
import requests
from celery import shared_task
from django.db import transaction
from django.db.models import Q
from ai_services.stt_service import WhisperClient
from ai_services.llm_service import FinancialAI
from finance.models import Transaction, Category, Account

logger = logging.getLogger(__name__)

# Инициализируем сервисы один раз при запуске воркера
whisper = WhisperClient()
ai_assistant = FinancialAI()

BOT_TOKEN = os.environ.get("BOT_TOKEN")

def send_telegram_message(chat_id, text):
    """
    Sends a message to a specific Telegram chat using the Telegram Bot API.
    
    Args:
        chat_id (str/int): The ID of the Telegram chat to send the message to.
        text (str): The content of the message to be sent.
    """
    logger.info(f"DEBUG: Attempting to send Telegram message. chat_id={chat_id}, BOT_TOKEN={'Found' if BOT_TOKEN else 'Missing'}")
    
    if not chat_id or not BOT_TOKEN:
        logger.warning(f"Cannot send Telegram notification: chat_id={chat_id}, BOT_TOKEN={'Found' if BOT_TOKEN else 'Missing'}")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {e}")

@shared_task(
    bind=True, 
    max_retries=3, 
    autoretry_for=(requests.RequestException,), # Only retry on network errors
    retry_backoff=True
)
def process_voice_transaction_task(self, user_id, file_path, account_id, chat_id=None):
    """
    Celery task that processes a voice message, transcribes it to text,
    parses it into a transaction, and saves it. Also cleans up the temporary audio file.
    
    Args:
        user_id (int): The ID of the user creating the transaction.
        file_path (str): The path to the temporary audio file.
        account_id (int): The ID of the account the transaction belongs to.
        chat_id (str/int, optional): The Telegram chat ID to notify upon success or failure.
        
    Returns:
        str: A message indicating the result of the processing.
    """
    should_delete = True
    try:
        # 1. Транскрибация (Голос -> Текст)
        # Файл еще на диске, передаем путь в Whisper
        raw_text = whisper.transcribe(file_path)
        
        if not raw_text:
            logger.warning(f"Whisper не смог распознать текст в файле: {file_path}")
            if chat_id:
                send_telegram_message(chat_id, "⚠️ Could not recognize any speech in the voice message.")
            return "Empty audio"

        result_message = _process_transaction_from_text(user_id, raw_text, account_id)
        if chat_id:
            send_telegram_message(chat_id, f"✅ {result_message}")
        return result_message

    except Exception as exc:
        logger.error(f"Ошибка при обработке транзакции: {exc}")
        # If it's a network error, we might want to retry, but we need the file!
        # Since we use autoretry_for=(requests.RequestException,), 
        # it will only reach here for other exceptions or after manual retry call.
        if isinstance(exc, requests.RequestException):
             should_delete = False # Keep file for retry
        
        if chat_id:
            send_telegram_message(chat_id, f"❌ Error processing voice transaction: {exc}")
        raise exc

    finally:
        # 5. ОПТИМИЗАЦИЯ: Удаление файла
        if should_delete and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Временный файл удален: {file_path}")
            except OSError as e:
                logger.error(f"Критическая ошибка при удалении файла {file_path}: {e}")

@shared_task(
    bind=True, 
    max_retries=3, 
    autoretry_for=(Exception,), 
    retry_backoff=True
)
def process_text_transaction_task(self, user_id, text, account_id, chat_id=None):
    """
    Celery task that processes a text message into a transaction and saves it.
    
    Args:
        user_id (int): The ID of the user creating the transaction.
        text (str): The text description of the transaction.
        account_id (int): The ID of the account the transaction belongs to.
        chat_id (str/int, optional): The Telegram chat ID to notify upon success or failure.
        
    Returns:
        str: A message indicating the result of the processing.
    """
    try:
        result_message = _process_transaction_from_text(user_id, text, account_id)
        if chat_id:
            send_telegram_message(chat_id, f"✅ {result_message}")
        return result_message
    except Exception as exc:
        logger.error(f"Ошибка при обработке текстовой транзакции: {exc}")
        if chat_id:
             send_telegram_message(chat_id, f"❌ Error processing text transaction: {exc}")
        raise exc

def _process_transaction_from_text(user_id, raw_text, account_id):
    """
    Core logic to parse a transaction text using the AI service, map it to an existing
    or new category, and store the resulting Transaction in the database.
    
    Args:
        user_id (int): The ID of the user.
        raw_text (str): The transaction description text.
        account_id (int): The ID of the target account.
        
    Returns:
        str: A string summarizing the created transaction.
    """
    from user_auth.models import User
    user = User.objects.get(id=user_id)
    default_currency = user.base_currency

    # 2. Подготовка данных для LLM
    # Берем категории юзера И общие категории
    categories_qs = Category.objects.filter(Q(user_id=user_id) | Q(user__isnull=True))
    categories = list(categories_qs.values_list('name', flat=True))

    # 3. Извлечение структуры (Текст -> JSON)
    ai_data = ai_assistant.parse_transaction(raw_text, categories, default_currency=default_currency)

    # 4. Сохранение в БД
    with transaction.atomic():
        category_name = ai_data.get('category', 'Other')
        parsed_currency_code = ai_data.get('currency', default_currency)
        
        # Пытаемся найти категорию (свою или общую)
        category = Category.objects.filter(
            Q(user_id=user_id) | Q(user__isnull=True),
            name__iexact=category_name
        ).first()

        if not category:
            # Если не нашли, ищем категорию "Other" (или "Другое")
            category = Category.objects.filter(
                Q(user_id=user_id) | Q(user__isnull=True),
                name__in=['Other', 'Другое']
            ).first()

        if not category:
            # Если совсем ничего нет, создаем новую категорию "Other" для юзера
            category = Category.objects.create(
                user_id=user_id,
                name='Other',
                type='EXPENSE', # Default to expense
                is_essential=False
            )

        account = Account.objects.get(id=account_id)
        
        new_trans = Transaction.objects.create(
            user_id=user_id,
            account=account,
            category=category,
            amount_original=ai_data.get('amount', 0),
            amount_base=ai_data.get('amount', 0), 
            description=ai_data.get('description', ''),
            raw_text=raw_text
        )
    
    return f"Transaction created:\nAmount: {new_trans.amount_original} {parsed_currency_code}\nCategory: {category.name}\nDesc: {new_trans.description}"