"""
Обработчики выбора категорий и подкатегорий
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from models import UserState
from keyboards import get_subcategories_keyboard, get_results_keyboard
from services import TermsService
from utils.texts import get_text, translate_category
from utils.formatter import format_results_page

router = Router()
terms_service = TermsService()


@router.callback_query(F.data.startswith("cat:"))
async def handle_category_selection(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора категории
    
    Args:
        callback: Callback от inline кнопки
        state: FSM состояние пользователя
    """
    # Извлекаем название категории из callback_data
    category = callback.data.split(":", 1)[1]  # "cat:Медицина" -> "Медицина"
    
    # Получаем текущий язык
    data = await state.get_data()
    lang = data.get('language', 'kk')
    
    # Сохраняем выбранную категорию
    await state.update_data(selected_category=category)
    
    # Получаем список подкатегорий
    subcategories = terms_service.get_subcategories(category, lang=lang)
    
    if not subcategories:
        await callback.answer(
            get_text('category_empty', lang),
            show_alert=True
        )
        return
    
    # Переходим к выбору подкатегории
    await state.set_state(UserState.choosing_subcategory)
    
    # Формируем сообщение и клавиатуру
    # Переводим название категории для отображения в сообщении
    category_display = translate_category(category, lang) if lang == 'ru' else category
    message_text = get_text('choose_subcategory', lang, category=category_display)
    keyboard = get_subcategories_keyboard(subcategories, lang=lang)
    
    # Обновляем сообщение
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith("sub:"))
async def handle_subcategory_selection(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора подкатегории
    
    Args:
        callback: Callback от inline кнопки
        state: FSM состояние пользователя
    """
    # Извлекаем название подкатегории из callback_data
    subcategory = callback.data.split(":", 1)[1]  # "sub:Емхана" -> "Емхана"
    
    # Получаем текущие данные
    data = await state.get_data()
    lang = data.get('language', 'kk')
    category = data.get('selected_category', '')
    
    # Сохраняем выбранную подкатегорию и сбрасываем страницу
    await state.update_data(
        selected_subcategory=subcategory,
        current_page=1
    )
    
    # Получаем термины из выбранной категории/подкатегории
    terms = terms_service.get_terms_by_category(category, subcategory, lang=lang)
    
    if not terms:
        await callback.answer(
            get_text('no_results', lang),
            show_alert=True
        )
        return
    
    # Сохраняем результаты в состоянии
    await state.update_data(current_results=terms)
    
    # Переходим к просмотру результатов
    await state.set_state(UserState.viewing_results)
    
    # Формируем сообщение с результатами
    per_page = 10
    total_count = len(terms)
    
    header = get_text('results_found', lang, count=total_count) + "\n\n"
    results_text = format_results_page(terms, page=1, per_page=per_page, show_lang=False)
    
    message_text = header + results_text
    
    # Определяем, есть ли следующая страница
    has_next = total_count > per_page
    
    # Формируем клавиатуру
    keyboard = get_results_keyboard(
        lang=lang,
        has_prev=False,
        has_next=has_next,
        show_search=True
    )
    
    # Обновляем сообщение
    try:
        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    except Exception:
        # Если сообщение слишком длинное, отправляем новое
        await callback.message.delete()
        await callback.message.answer(
            text=message_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    await callback.answer()

