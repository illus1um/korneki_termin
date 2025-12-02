"""
Маппер категорий и подкатегорий для коротких callback_data
Использует паттерн Singleton для единственного экземпляра
"""
from typing import Dict, Optional


class CategoryMapper:
    """Класс для преобразования названий категорий в короткие ID и обратно (Singleton)"""
    
    _instance: Optional['CategoryMapper'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton - создаёт только один экземпляр"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Пропускаем повторную инициализацию
        if CategoryMapper._initialized:
            return
            
        self._cat_to_id: Dict[str, int] = {}
        self._id_to_cat: Dict[int, str] = {}
        self._subcat_to_id: Dict[str, int] = {}
        self._id_to_subcat: Dict[int, str] = {}
        self._next_cat_id = 1
        self._next_subcat_id = 1
        
        CategoryMapper._initialized = True
    
    def register_category(self, category: str) -> int:
        """
        Регистрирует категорию и возвращает её ID
        Если категория уже зарегистрирована, возвращает существующий ID
        """
        if category in self._cat_to_id:
            return self._cat_to_id[category]
            
        cat_id = self._next_cat_id
        self._cat_to_id[category] = cat_id
        self._id_to_cat[cat_id] = category
        self._next_cat_id += 1
        return cat_id
    
    def register_subcategory(self, subcategory: str) -> int:
        """
        Регистрирует подкатегорию и возвращает её ID
        Если подкатегория уже зарегистрирована, возвращает существующий ID
        """
        if subcategory in self._subcat_to_id:
            return self._subcat_to_id[subcategory]
            
        subcat_id = self._next_subcat_id
        self._subcat_to_id[subcategory] = subcat_id
        self._id_to_subcat[subcat_id] = subcategory
        self._next_subcat_id += 1
        return subcat_id
    
    def get_category_id(self, category: str) -> Optional[int]:
        """Получить ID категории по названию"""
        return self._cat_to_id.get(category)
    
    def get_category_name(self, cat_id: int) -> Optional[str]:
        """Получить название категории по ID"""
        return self._id_to_cat.get(cat_id)
    
    def get_subcategory_id(self, subcategory: str) -> Optional[int]:
        """Получить ID подкатегории по названию"""
        return self._subcat_to_id.get(subcategory)
    
    def get_subcategory_name(self, subcat_id: int) -> Optional[str]:
        """Получить название подкатегории по ID"""
        return self._id_to_subcat.get(subcat_id)
    
    def is_initialized(self) -> bool:
        """Проверить, инициализирован ли маппер данными"""
        return len(self._cat_to_id) > 0


# Глобальная функция для получения маппера
def get_mapper() -> CategoryMapper:
    """Получить глобальный экземпляр маппера"""
    return CategoryMapper()
