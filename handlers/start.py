"""
Обработчик команды /start
"""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Обработчик команды /start
    
    Args:
        message: Входящее сообщение
    """
    welcome_text = (
        "👋 Сәлеметсіз бе! Мен терминдерді іздеу ботымын.\n\n"
        "📝 Маған кез келген мәтінді жіберіңіз, мен деректер базасынан сәйкес терминдерді табамын.\n\n"
        "💡 Мысалы, мынаны енгізіп көріңіз: Салауат"
    )
    
    await message.answer(welcome_text)

