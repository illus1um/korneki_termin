"""
Сервис для работы с терминами из CSV файла
Использует паттерн Singleton для единственного экземпляра
"""
import csv
from typing import List, Dict, Set, Optional
from pathlib import Path
from utils.logger import get_logger

logger = get_logger('services.terms_service')


class TermsService:
    """Сервис для загрузки и поиска терминов (Singleton)"""
    
    _instance: Optional['TermsService'] = None
    _initialized: bool = False
    
    def __new__(cls, csv_path: str = 'data/extracted_terms_full.csv'):
        """Singleton - создаёт только один экземпляр"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, csv_path: str = 'data/extracted_terms_full.csv'):
        """
        Инициализация сервиса (выполняется только один раз)
        
        Args:
            csv_path: Путь к CSV файлу с терминами
        """
        # Пропускаем повторную инициализацию
        if TermsService._initialized:
            return
            
        self.csv_path = Path(csv_path)
        self.terms: List[Dict[str, str]] = []
        
        # Кэши для ускорения работы
        self._categories_cache: Dict[str, List[str]] = {}
        self._subcategories_cache: Dict[str, List[str]] = {}
        self._terms_cache: Dict[str, List[Dict[str, str]]] = {}  # Кэш терминов по категориям/подкатегориям
        
        self._load_terms()
        TermsService._initialized = True
    
    def _load_terms(self) -> None:
        """Загружает термины из CSV файла в память"""
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, quoting=csv.QUOTE_MINIMAL)
                self.terms = []
                for row in reader:
                    # Пропускаем строки с пустыми ключами
                    cleaned_row = {}
                    for key, value in row.items():
                        if key is not None:
                            clean_key = key.strip() if key else ''
                            clean_value = value.strip() if value else ''
                            if clean_key:  # Только если ключ не пустой
                                cleaned_row[clean_key] = clean_value
                    
                    # Добавляем только если есть термин
                    if cleaned_row.get('term'):
                        self.terms.append(cleaned_row)
                        
            logger.info(f"Загружено {len(self.terms)} терминов из {self.csv_path}")
            
            # Предварительно кэшируем категории
            self._build_cache()
            
        except FileNotFoundError:
            logger.error(f"Файл {self.csv_path} не найден")
            self.terms = []
        except Exception as e:
            logger.error(f"Ошибка при загрузке CSV: {e}", exc_info=True)
            self.terms = []
    
    def _build_cache(self) -> None:
        """Строит кэш категорий, подкатегорий и терминов для быстрого доступа O(1)"""
        for lang in ['kk', 'ru']:
            categories: Set[str] = set()
            
            for term in self.terms:
                term_lang = term.get('lang', '').strip()
                if term_lang == lang:
                    cat = term.get('category', '').strip()
                    subcat = term.get('subcategory', '').strip()
                    
                    if cat:
                        categories.add(cat)
                        
                        # Кэш подкатегорий
                        cache_key_subcat = f"{cat}:{lang}"
                        if cache_key_subcat not in self._subcategories_cache:
                            self._subcategories_cache[cache_key_subcat] = set()
                        if subcat:
                            self._subcategories_cache[cache_key_subcat].add(subcat)
                        
                        # Кэш терминов по категории/подкатегории/языку
                        if subcat:
                            cache_key_terms = f"{cat}:{subcat}:{lang}"
                            if cache_key_terms not in self._terms_cache:
                                self._terms_cache[cache_key_terms] = []
                            self._terms_cache[cache_key_terms].append(term)
            
            self._categories_cache[lang] = sorted(list(categories))
        
        # Преобразуем set в list для подкатегорий
        for key in self._subcategories_cache:
            self._subcategories_cache[key] = sorted(list(self._subcategories_cache[key]))
        
        logger.info(f"Кэш построен: {len(self._terms_cache)} групп терминов")
    
    def get_categories(self, lang: str = 'kk') -> List[str]:
        """
        Получить список всех уникальных категорий (из кэша)
        
        Args:
            lang: Язык для фильтрации ('kk' или 'ru')
            
        Returns:
            Отсортированный список уникальных категорий
        """
        return self._categories_cache.get(lang, [])
    
    def get_subcategories(self, category: str, lang: str = 'kk') -> List[str]:
        """
        Получить список подкатегорий для указанной категории (из кэша)
        
        Args:
            category: Название категории
            lang: Язык для фильтрации ('kk' или 'ru')
            
        Returns:
            Отсортированный список уникальных подкатегорий
        """
        cache_key = f"{category}:{lang}"
        return self._subcategories_cache.get(cache_key, [])
    
    def get_terms_by_category(
        self,
        category: str,
        subcategory: str,
        lang: str = 'kk'
    ) -> List[Dict[str, str]]:
        """
        Получить все термины из указанной категории и подкатегории
        Оптимизировано: O(1) доступ из кэша вместо O(n) поиска
        
        Args:
            category: Название категории
            subcategory: Название подкатегории
            lang: Язык для фильтрации ('kk' или 'ru')
            
        Returns:
            Список терминов из указанной категории/подкатегории
        """
        cache_key = f"{category}:{subcategory}:{lang}"
        return self._terms_cache.get(cache_key, [])
    
    def search_in_filtered(
        self,
        query: str,
        category: str,
        subcategory: str,
        lang: str = 'kk',
        max_results: int = None
    ) -> List[Dict[str, str]]:
        """
        Поиск терминов внутри отфильтрованной выборки
        Оптимизировано: использует кэш терминов вместо прохода по всем терминам
        """
        from config import settings
        
        if not query:
            return []
        
        # Используем значение из конфига если не указано
        if max_results is None:
            max_results = settings.MAX_SEARCH_RESULTS
        
        # Получаем термины из кэша O(1) вместо прохода по всем терминам O(n)
        cache_key = f"{category}:{subcategory}:{lang}"
        filtered_terms = self._terms_cache.get(cache_key, [])
        
        if not filtered_terms:
            return []
        
        query_lower = query.lower().strip()
        exact_matches = []
        partial_matches = []
        description_matches = []
        
        # Ищем только в отфильтрованных терминах (обычно 10-200 штук вместо 8000)
        for term in filtered_terms:
            term_name = term.get('term', '').lower()
            description = term.get('description', '').lower()
            
            if term_name == query_lower:
                exact_matches.append(term)
            elif query_lower in term_name:
                partial_matches.append(term)
            elif query_lower in description:
                description_matches.append(term)
        
        results = exact_matches + partial_matches + description_matches
        return results[:max_results]
