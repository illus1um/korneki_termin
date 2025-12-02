"""
Обработчик команды /start и /menu
"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from models import UserState
from keyboards import get_language_keyboard, get_categories_keyboard, get_subcategories_keyboard
from services import TermsService
from utils.texts import get_text, WELCOME_BILINGUAL

router = Router()
terms_service = TermsService()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    Обработчик команды /start
    Показывает двуязычное приветствие и предлагает выбрать язык
    
    Args:
        message: Входящее сообщение
        state: FSM состояние пользователя
    """
    # Сбрасываем состояние
    await state.clear()
    
    # Переходим в состояние выбора языка
    await state.set_state(UserState.choosing_language)
    
    # Отправляем двуязычное приветствие с кнопками выбора языка
    keyboard = get_language_keyboard()
    
    await message.answer(
        text=WELCOME_BILINGUAL,
        reply_markup=keyboard
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    """
    Обработчик команды /menu
    Возвращает пользователя в главное меню (выбор категории)
    
    Args:
        message: Входящее сообщение
        state: FSM состояние пользователя
    """
    # Получаем текущий язык
    data = await state.get_data()
    lang = data.get('language', 'kk')
    
    # Переходим к выбору категории
    await state.set_state(UserState.choosing_category)
    
    # Очищаем предыдущие выборки
    await state.update_data(
        selected_category=None,
        selected_subcategory=None,
        current_page=1,
        current_results=[]
    )
    
    # Получаем список категорий
    categories = terms_service.get_categories(lang=lang)
    
    # Формируем сообщение и клавиатуру
    message_text = get_text('choose_category', lang)
    keyboard = get_categories_keyboard(categories, lang=lang)
    
    await message.answer(
        text=message_text,
        reply_markup=keyboard
    )


@router.callback_query(F.data == "action:home")
async def handle_home_action(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Главная"
    Возвращает пользователя к выбору категории
    
    Args:
        callback: Callback от inline кнопки
        state: FSM состояние пользователя
    """
    # Получаем текущий язык
    data = await state.get_data()
    lang = data.get('language', 'kk')
    
    # Переходим к выбору категории
    await state.set_state(UserState.choosing_category)
    
    # Очищаем предыдущие выборки
    await state.update_data(
        selected_category=None,
        selected_subcategory=None,
        current_page=1,
        current_results=[]
    )
    
    # Получаем список категорий
    categories = terms_service.get_categories(lang=lang)
    
    # Формируем сообщение и клавиатуру
    message_text = get_text('choose_category', lang)
    keyboard = get_categories_keyboard(categories, lang=lang)
    
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard
    )
    
    await callback.answer()


@router.callback_query(F.data == "action:back")
async def handle_back_action(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Назад"
    Возвращает пользователя на предыдущий шаг
    
    Args:
        callback: Callback от inline кнопки
        state: FSM состояние пользователя
    """
    current_state = await state.get_state()
    data = await state.get_data()
    lang = data.get('language', 'kk')
    
    # Если просматриваем результаты или в режиме поиска -> возврат к подкатегориям
    if current_state in [UserState.viewing_results, UserState.searching_in_results]:
        category = data.get('selected_category', '')
        subcategories = terms_service.get_subcategories(category, lang=lang)
        
        await state.set_state(UserState.choosing_subcategory)
        await state.update_data(
            selected_subcategory=None,
            current_page=1,
            current_results=[]
        )
        
        message_text = get_text('choose_subcategory', lang, category=category)
        keyboard = get_subcategories_keyboard(subcategories, lang=lang)
        
        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard
        )
    
    # Если выбираем подкатегорию -> возврат к категориям
    elif current_state == UserState.choosing_subcategory:
        categories = terms_service.get_categories(lang=lang)
        
        await state.set_state(UserState.choosing_category)
        await state.update_data(selected_category=None)
        
        message_text = get_text('choose_category', lang)
        keyboard = get_categories_keyboard(categories, lang=lang)
        
        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard
        )
    
    # В остальных случаях -> главное меню
    else:
        categories = terms_service.get_categories(lang=lang)
        
        await state.set_state(UserState.choosing_category)
        
        message_text = get_text('choose_category', lang)
        keyboard = get_categories_keyboard(categories, lang=lang)
        
        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard
        )
    
    await callback.answer()

