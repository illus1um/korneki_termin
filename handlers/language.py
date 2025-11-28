"""
Обработчик смены языка
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from models import UserState
from keyboards import get_categories_keyboard
from services import TermsService
from utils.texts import get_text

router = Router()
terms_service = TermsService()


@router.callback_query(F.data.startswith("lang:"))
async def handle_language_selection(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора языка интерфейса
    
    Args:
        callback: Callback от inline кнопки
        state: FSM состояние пользователя
    """
    # Извлекаем код языка из callback_data
    lang = callback.data.split(":")[1]  # "lang:kk" -> "kk"
    
    # Сохраняем выбранный язык в состоянии
    await state.update_data(language=lang)
    
    # Переходим к выбору категории
    await state.set_state(UserState.choosing_category)
    
    # Получаем список категорий на выбранном языке
    categories = terms_service.get_categories(lang=lang)
    
    # Формируем сообщение и клавиатуру
    message_text = get_text('choose_category', lang)
    keyboard = get_categories_keyboard(categories, lang=lang)
    
    # Обновляем сообщение
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard
    )
    
    await callback.answer()


@router.callback_query(F.data == "action:change_lang")
async def handle_change_language(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки смены языка
    
    Args:
        callback: Callback от inline кнопки
        state: FSM состояние пользователя
    """
    from keyboards import get_language_keyboard
    
    # Получаем текущий язык
    data = await state.get_data()
    current_lang = data.get('language', 'kk')
    
    # Показываем клавиатуру выбора языка
    message_text = get_text('choose_language', current_lang)
    keyboard = get_language_keyboard()
    
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard
    )
    
    await callback.answer()

