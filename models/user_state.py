"""
Состояния пользователя для FSM (Finite State Machine)
"""
from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    """
    Состояния пользователя при работе с ботом
    
    Переходы между состояниями:
    choosing_language → choosing_category → choosing_subcategory → viewing_results
                                                                    ↓
                                                            searching_in_results
    """
    
    # Выбор языка интерфейса
    choosing_language = State()
    
    # Выбор основной категории (из 18)
    choosing_category = State()
    
    # Выбор подкатегории
    choosing_subcategory = State()
    
    # Просмотр результатов (список терминов)
    viewing_results = State()
    
    # Поиск внутри отфильтрованных результатов
    searching_in_results = State()

