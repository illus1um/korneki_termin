"""
Обработчик поиска терминов
"""
from aiogram import Router
from aiogram.types import Message
from aiogram.enums import ParseMode

from services import TermsService
from utils import format_term

router = Router()

# Инициализируем сервис терминов
terms_service = TermsService()


@router.message()
async def search_terms(message: Message):
    """
    Обработчик текстовых сообщений для поиска терминов
    
    Args:
        message: Входящее сообщение
    """
    query = message.text
    
    if not query:
        await message.answer("❌ Іздеу үшін мәтін енгізіңіз")
        return
    
    # Выполняем поиск
    results = terms_service.search(query)
    
    if not results:
        await message.answer(
            f"🔍 «{query}» сұранысы бойынша ештеңе табылмады.\n"
            "Басқа іздеу сұранысын қолданып көріңіз."
        )
        return
    
    # Формируем ответ
    response_parts = [f"🔍 Табылған нәтижелер саны: {len(results)}\n"]
    
    for i, term_data in enumerate(results, 1):
        formatted_term = format_term(term_data)
        response_parts.append(f"{i}. {formatted_term}")
    
    response = "\n\n".join(response_parts)
    
    # Отправляем ответ с Markdown форматированием
    await message.answer(response, parse_mode=ParseMode.MARKDOWN)

