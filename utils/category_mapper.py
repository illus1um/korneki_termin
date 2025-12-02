"""
Маппер категорий и подкатегорий для коротких callback_data
"""
from typing import Dict, Optional


class CategoryMapper:
    """Класс для преобразования названий категорий в короткие ID и обратно"""
    
    def __init__(self):
        self._cat_to_id: Dict[str, int] = {}
        self._id_to_cat: Dict[int, str] = {}
        self._subcat_to_id: Dict[str, int] = {}
        self._id_to_subcat: Dict[int, str] = {}
        self._next_cat_id = 1
        self._next_subcat_id = 1
    
    def register_category(self, category: str) -> int:
        """
        Регистрирует категорию и возвращает её ID
        
        Args:
            category: Название категории
            
        Returns:
            ID категории
        """
        if category not in self._cat_to_id:
            cat_id = self._next_cat_id
            self._cat_to_id[category] = cat_id
            self._id_to_cat[cat_id] = category
            self._next_cat_id += 1
            return cat_id
        return self._cat_to_id[category]
    
    def register_subcategory(self, subcategory: str) -> int:
        """
        Регистрирует подкатегорию и возвращает её ID
        
        Args:
            subcategory: Название подкатегории
            
        Returns:
            ID подкатегории
        """
        if subcategory not in self._subcat_to_id:
            subcat_id = self._next_subcat_id
            self._subcat_to_id[subcategory] = subcat_id
            self._id_to_subcat[subcat_id] = subcategory
            self._next_subcat_id += 1
            return subcat_id
        return self._subcat_to_id[subcategory]
    
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
    
    def initialize_from_service(self, terms_service):
        """
        Инициализирует маппер из TermsService
        
        Args:
            terms_service: Экземпляр TermsService
        """
        # Регистрируем все категории
        categories = terms_service.get_categories('kk')
        for cat in categories:
            self.register_category(cat)
        
        # Регистрируем все подкатегории
        for cat in categories:
            subcategories = terms_service.get_subcategories(cat, 'kk')
            for subcat in subcategories:
                self.register_subcategory(subcat)


# Глобальный экземпляр маппера
_mapper = CategoryMapper()


def get_mapper() -> CategoryMapper:
    """Получить глобальный экземпляр маппера"""
    return _mapper

