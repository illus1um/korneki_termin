"""
Сервис для работы с терминами из CSV файла
"""
import csv
from typing import List, Dict, Set
from pathlib import Path


class TermsService:
    """Сервис для загрузки и поиска терминов"""
    
    def __init__(self, csv_path: str = 'data/extracted_terms_full.csv'):
        """
        Инициализация сервиса
        
        Args:
            csv_path: Путь к CSV файлу с терминами
        """
        self.csv_path = Path(csv_path)
        self.terms: List[Dict[str, str]] = []
        self._load_terms()
    
    def _load_terms(self) -> None:
        """Загружает термины из CSV файла в память"""
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                # Используем quoting=csv.QUOTE_MINIMAL для корректной обработки запятых
                reader = csv.DictReader(file, quoting=csv.QUOTE_MINIMAL)
                # Очищаем данные от лишних пробелов
                self.terms = []
                for row in reader:
                    cleaned_row = {
                        key.strip(): value.strip() if value else '' 
                        for key, value in row.items()
                    }
                    self.terms.append(cleaned_row)
            print(f"[OK] Загружено {len(self.terms)} терминов из {self.csv_path}")
        except FileNotFoundError:
            print(f"[ERROR] Файл {self.csv_path} не найден")
            self.terms = []
        except Exception as e:
            print(f"[ERROR] Ошибка при загрузке CSV: {e}")
            self.terms = []
    
    def get_categories(self, lang: str = 'kk') -> List[str]:
        """
        Получить список всех уникальных категорий
        
        Args:
            lang: Язык для фильтрации ('kk' или 'ru')
            
        Returns:
            Отсортированный список уникальных категорий
        """
        categories: Set[str] = set()
        
        for term in self.terms:
            if term.get('lang') == lang:
                category = term.get('category', '').strip()
                if category:
                    categories.add(category)
        
        return sorted(list(categories))
    
    def get_subcategories(self, category: str, lang: str = 'kk') -> List[str]:
        """
        Получить список подкатегорий для указанной категории
        
        Args:
            category: Название категории
            lang: Язык для фильтрации ('kk' или 'ru')
            
        Returns:
            Отсортированный список уникальных подкатегорий
        """
        subcategories: Set[str] = set()
        
        for term in self.terms:
            if (term.get('category') == category and 
                term.get('lang') == lang):
                subcategory = term.get('subcategory', '').strip()
                if subcategory:
                    subcategories.add(subcategory)
        
        return sorted(list(subcategories))
    
    def get_terms_by_category(
        self,
        category: str,
        subcategory: str,
        lang: str = 'kk'
    ) -> List[Dict[str, str]]:
        """
        Получить все термины из указанной категории и подкатегории
        
        Args:
            category: Название категории
            subcategory: Название подкатегории
            lang: Язык для фильтрации ('kk' или 'ru')
            
        Returns:
            Список терминов из указанной категории/подкатегории
        """
        results = []
        
        for term in self.terms:
            if (term.get('category') == category and
                term.get('subcategory') == subcategory and
                term.get('lang') == lang):
                results.append(term)
        
        return results
    
    def search_in_filtered(
        self,
        query: str,
        category: str,
        subcategory: str,
        lang: str = 'kk',
        max_results: int = 50
    ) -> List[Dict[str, str]]:
        """
        Поиск терминов внутри отфильтрованной выборки
        
        Args:
            query: Поисковый запрос
            category: Категория для фильтрации
            subcategory: Подкатегория для фильтрации
            lang: Язык для фильтрации
            max_results: Максимальное количество результатов
            
        Returns:
            Список найденных терминов
        """
        if not query:
            return []
        
        query_lower = query.lower().strip()
        exact_matches = []
        partial_matches = []
        description_matches = []
        
        for term in self.terms:
            # Проверяем фильтры
            if not (term.get('category') == category and
                    term.get('subcategory') == subcategory and
                    term.get('lang') == lang):
                continue
            
            term_name = term.get('term', '').lower()
            description = term.get('description', '').lower()
            
            # Точное совпадение в названии
            if term_name == query_lower:
                exact_matches.append(term)
            # Частичное совпадение в названии
            elif query_lower in term_name:
                partial_matches.append(term)
            # Совпадение в описании
            elif query_lower in description:
                description_matches.append(term)
        
        # Возвращаем результаты в порядке приоритета
        results = exact_matches + partial_matches + description_matches
        
        return results[:max_results]
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Глобальный поиск терминов по запросу (устаревший метод, оставлен для совместимости)
        
        Выполняет:
        1. Точный поиск (term == query)
        2. Частичный поиск (query in term)
        
        Args:
            query: Поисковый запрос
            max_results: Максимальное количество результатов (по умолчанию 5)
            
        Returns:
            Список найденных терминов (максимум max_results)
        """
        if not query:
            return []
        
        query_lower = query.lower().strip()
        exact_matches = []
        partial_matches = []
        
        for term in self.terms:
            term_name = term.get('term', '').lower()
            
            # Точное совпадение
            if term_name == query_lower:
                exact_matches.append(term)
            # Частичное совпадение
            elif query_lower in term_name:
                partial_matches.append(term)
        
        # Возвращаем сначала точные совпадения, потом частичные
        results = exact_matches + partial_matches
        
        # Ограничиваем количество результатов
        return results[:max_results]

