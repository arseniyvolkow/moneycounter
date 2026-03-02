from pydantic import BaseModel, Field
from typing import Optional, List


class TransactionSchema(BaseModel):
    """
    Pydantic schema representing the structure of a financial transaction.
    Used for validating LLM output.
    """
    amount: float = Field(description="Числовое значение суммы")
    currency: str = Field(description="ISO код валюты, по умолчанию KZT")
    category: str = Field(
        description="Категория (Продукты, Транспорт, Жилье, Доход и т.д.)"
    )
    merchant: Optional[str] = Field(description="Название магазина или сервиса")
    is_income: bool = Field(description="True если это доход, False если расход")
    description: Optional[str] = Field(description="Краткое описание на основе текста")


class TransactionRequest(BaseModel):
    """
    Pydantic schema for an incoming transaction request to the AI service.
    """
    text: str
    available_categories: List[str]  # Список названий категорий из твоей БД