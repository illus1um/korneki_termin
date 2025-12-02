"""
Обработчики выбора категорий и подкатегорий
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from models import UserState
from keyboards import get_subcategories_keyboard, get_results_keyboard
from services import TermsService
from utils.texts import get_text, translate_category, translate_subcategory
from utils.formatter import format_results_page
from utils.category_mapper import get_mapper

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
    # Извлекаем ID категории из callback_data и преобразуем в название
    cat_id_str = callback.data.split(":", 1)[1]  # "cat:1" -> "1"
    cat_id = int(cat_id_str)
    mapper = get_mapper()
    category = mapper.get_category_name(cat_id)
    
    if not category:
        await callback.answer("❌ Ошибка: категория не найдена", show_alert=True)
        return
    
    # Получаем текущий язык
    data = await state.get_data()
    lang = data.get('language', 'kk')
    
    # Сохраняем выбранную категорию
    await state.update_data(selected_category=category)
    
    # Получаем список подкатегорий для текущего языка
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
    # Извлекаем ID подкатегории из callback_data и преобразуем в название
    subcat_id_str = callback.data.split(":", 1)[1]  # "sub:1" -> "1"
    subcat_id = int(subcat_id_str)
    mapper = get_mapper()
    subcategory = mapper.get_subcategory_name(subcat_id)
    
    if not subcategory:
        await callback.answer("❌ Ошибка: подкатегория не найдена", show_alert=True)
        return
    
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
    # ВАЖНО: фильтруем по выбранному языку интерфейса
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
    
    # Формируем заголовок с категорией и подкатегорией (с переводом)
    category_display = translate_category(category, lang) if lang == 'ru' else category
    subcategory_display = translate_subcategory(subcategory, lang) if lang == 'ru' else subcategory
    header = get_text('results_found', lang, count=total_count)
    header += f"\n📂 {category_display} / {subcategory_display}\n\n"
    
    results_text = format_results_page(terms, page=1, per_page=per_page, show_lang=False, show_category=False)
    
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

