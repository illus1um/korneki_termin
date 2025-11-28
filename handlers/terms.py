"""
Обработчики для просмотра результатов, пагинации и поиска
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from models import UserState
from services import TermsService
from keyboards import get_results_keyboard, get_search_keyboard
from utils.texts import get_text
from utils.formatter import format_results_page

router = Router()
terms_service = TermsService()


@router.callback_query(F.data == "action:search")
async def handle_search_action(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Поиск" - включает режим поиска внутри результатов
    
    Args:
        callback: Callback от inline кнопки
        state: FSM состояние пользователя
    """
    data = await state.get_data()
    lang = data.get('language', 'kk')
    subcategory = data.get('selected_subcategory', '')
    
    # Переходим в режим поиска
    await state.set_state(UserState.searching_in_results)
    
    # Формируем сообщение
    message_text = get_text('search_mode_on', lang, subcategory=subcategory)
    keyboard = get_search_keyboard(lang=lang)
    
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard
    )
    
    await callback.answer()


@router.callback_query(F.data == "action:cancel_search")
async def handle_cancel_search(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Отмена поиска" - возврат к просмотру результатов
    
    Args:
        callback: Callback от inline кнопки
        state: FSM состояние пользователя
    """
    data = await state.get_data()
    lang = data.get('language', 'kk')
    current_results = data.get('current_results', [])
    current_page = data.get('current_page', 1)
    
    # Возвращаемся к просмотру результатов
    await state.set_state(UserState.viewing_results)
    
    # Формируем сообщение с результатами
    per_page = 10
    total_count = len(current_results)
    
    header = get_text('results_found', lang, count=total_count) + "\n\n"
    results_text = format_results_page(current_results, page=current_page, per_page=per_page)
    
    message_text = header + results_text
    
    # Определяем пагинацию
    has_prev = current_page > 1
    has_next = current_page * per_page < total_count
    
    keyboard = get_results_keyboard(
        lang=lang,
        has_prev=has_prev,
        has_next=has_next,
        show_search=True
    )
    
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await callback.answer()


@router.message(UserState.searching_in_results)
async def handle_search_query(message: Message, state: FSMContext):
    """
    Обработчик текстового ввода в режиме поиска
    Ищет внутри отфильтрованных результатов
    
    Args:
        message: Входящее сообщение
        state: FSM состояние пользователя
    """
    query = message.text
    
    if not query or not query.strip():
        return
    
    # Получаем данные из состояния
    data = await state.get_data()
    lang = data.get('language', 'kk')
    category = data.get('selected_category', '')
    subcategory = data.get('selected_subcategory', '')
    
    # Выполняем поиск внутри текущей выборки
    results = terms_service.search_in_filtered(
        query=query,
        category=category,
        subcategory=subcategory,
        lang=lang
    )
    
    if not results:
        # Ничего не найдено
        no_results_text = get_text('no_results_in_filter', lang, query=query)
        keyboard = get_search_keyboard(lang=lang)
        
        await message.answer(
            text=no_results_text,
            reply_markup=keyboard
        )
        return
    
    # Сохраняем результаты поиска и сбрасываем страницу
    await state.update_data(
        current_results=results,
        current_page=1
    )
    
    # Возвращаемся к просмотру результатов
    await state.set_state(UserState.viewing_results)
    
    # Формируем сообщение с результатами
    per_page = 10
    total_count = len(results)
    
    header = get_text('search_results', lang, query=query, count=total_count) + "\n\n"
    results_text = format_results_page(results, page=1, per_page=per_page)
    
    message_text = header + results_text
    
    # Определяем пагинацию
    has_next = total_count > per_page
    
    keyboard = get_results_keyboard(
        lang=lang,
        has_prev=False,
        has_next=has_next,
        show_search=True
    )
    
    await message.answer(
        text=message_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "action:next_page")
async def handle_next_page(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Следующая страница"
    
    Args:
        callback: Callback от inline кнопки
        state: FSM состояние пользователя
    """
    data = await state.get_data()
    lang = data.get('language', 'kk')
    current_results = data.get('current_results', [])
    current_page = data.get('current_page', 1)
    
    per_page = 10
    total_pages = (len(current_results) + per_page - 1) // per_page
    
    # Переходим на следующую страницу
    next_page = min(current_page + 1, total_pages)
    await state.update_data(current_page=next_page)
    
    # Формируем сообщение
    total_count = len(current_results)
    header = get_text('results_found', lang, count=total_count) + "\n\n"
    results_text = format_results_page(current_results, page=next_page, per_page=per_page)
    
    message_text = header + results_text
    
    # Определяем пагинацию
    has_prev = next_page > 1
    has_next = next_page < total_pages
    
    keyboard = get_results_keyboard(
        lang=lang,
        has_prev=has_prev,
        has_next=has_next,
        show_search=True
    )
    
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await callback.answer()


@router.callback_query(F.data == "action:prev_page")
async def handle_prev_page(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Предыдущая страница"
    
    Args:
        callback: Callback от inline кнопки
        state: FSM состояние пользователя
    """
    data = await state.get_data()
    lang = data.get('language', 'kk')
    current_results = data.get('current_results', [])
    current_page = data.get('current_page', 1)
    
    per_page = 10
    total_pages = (len(current_results) + per_page - 1) // per_page
    
    # Переходим на предыдущую страницу
    prev_page = max(current_page - 1, 1)
    await state.update_data(current_page=prev_page)
    
    # Формируем сообщение
    total_count = len(current_results)
    header = get_text('results_found', lang, count=total_count) + "\n\n"
    results_text = format_results_page(current_results, page=prev_page, per_page=per_page)
    
    message_text = header + results_text
    
    # Определяем пагинацию
    has_prev = prev_page > 1
    has_next = prev_page < total_pages
    
    keyboard = get_results_keyboard(
        lang=lang,
        has_prev=has_prev,
        has_next=has_next,
        show_search=True
    )
    
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await callback.answer()

