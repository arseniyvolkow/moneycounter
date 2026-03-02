from thefuzz import process, fuzz
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .schemas import TransactionSchema
import logging

logger = logging.getLogger(__name__)

class FinancialAI:
    """
    A class responsible for interacting with an LLM (Language Model) 
    to parse natural language financial transactions into structured data.
    """
    def __init__(self, model_name="qwen2.5:3b", base_url="http://ollama:11434"):
        """
        Initializes the FinancialAI service.
        
        Args:
            model_name (str): The name of the LLM model to use (default: "qwen2.5:3b").
            base_url (str): The URL of the Ollama service hosting the model.
        """
        self.llm = ChatOllama(
            model=model_name,
            base_url=base_url,
            format="json",
            temperature=0
        )
        self.json_parser = JsonOutputParser(pydantic_object=TransactionSchema)

    def parse_transaction(self, text: str, categories: list, default_currency: str = "KZT"):
        """
        Parses a raw text transaction into a structured JSON dictionary using the LLM.
        
        Args:
            text (str): The raw text input describing the transaction.
            categories (list): A list of available categories to map the transaction to.
            default_currency (str): The default currency to use if none is specified in text.
            
        Returns:
            dict: A dictionary containing the parsed transaction details (amount, currency, category, etc.).
        """
        logger.info(f"Processing text: {text}")
        format_instructions = self.json_parser.get_format_instructions()

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Ты — финансовый парсер. Твоя задача — извлекать данные в формате JSON.\n" 
                       "ВАЖНО: Верни ТОЛЬКО объект с данными, не возвращай описание схемы.\n" 
                       "Выбирай категорию ТОЛЬКО из списка: {categories}.\n" 
                       "Если валюта не указана в тексте, используй валюту по умолчанию: {default_currency}.\n" 
                       "Если не уверен, выбери наиболее подходящую или 'Other'.\n" 
                       "{format_instructions}"),
            ("human", "{text}")
        ])

        chain = prompt | self.llm | self.json_parser
        
        try:
            result = chain.invoke({
                "text": text,
                "categories": categories,
                "default_currency": default_currency,
                "format_instructions": format_instructions
            })
            logger.info(f"LLM Result: {result}")
        except Exception as e:
            logger.error(f"Error invoking LLM chain: {e}")
            # Fallback result if parsing fails completely
            result = {}

        if not isinstance(result, dict):
             logger.warning(f"LLM returned non-dict result: {result}")
             result = {}
        
        # Handle nested 'properties' if LLM incorrectly returns schema structure
        if isinstance(result.get('properties'), dict):
            # If it's a schema definition, we try to extract default values or just fail gracefully
            # But usually it means the LLM failed. Let's try to extract if they are values.
            # If 'amount' inside 'properties' is a dict, it's a schema.
            first_val = next(iter(result['properties'].values()))
            if isinstance(first_val, dict):
                logger.warning("LLM returned schema definition instead of data")
                result = {}
            else:
                result = result['properties']

        # Ensure category exists and is a string
        ai_category = result.get('category', 'Other')
        if isinstance(ai_category, dict):
            # If LLM returned category as a dict (schema style), extract its title or just default
            ai_category = ai_category.get('title', 'Other')
        
        if not isinstance(ai_category, str):
            ai_category = str(ai_category)

        # Используем наш "приватный" метод для уточнения категории
        result['category'] = self._get_best_match(ai_category, categories)
        
        return result

    # Приватный метод (скрыт по соглашению именования)
    def _get_best_match(self, ai_category, categories, threshold=70):
        """
        Finds the closest matching category from the available categories using fuzzy string matching.
        
        Args:
            ai_category (str): The category string returned by the LLM.
            categories (list): The list of valid categories.
            threshold (int): The minimum match score required (default: 70).
            
        Returns:
            str: The best matching category name from the list, or "Other" if no good match is found.
        """
        if not categories or not isinstance(ai_category, str):
            return "Other"
        
        # Находим максимально похожее название из списка
        match, score = process.extractOne(ai_category, categories, scorer=fuzz.WRatio)
        return match if score >= threshold else "Other"
