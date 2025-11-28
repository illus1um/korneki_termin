"""
Сервис для работы с терминами из CSV файла
"""
import csv
from typing import List, Dict
from pathlib import Path


class TermsService:
    """Сервис для загрузки и поиска терминов"""
    
    def __init__(self, csv_path: str = 'data/terms_sample.csv'):
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
                reader = csv.DictReader(file)
                self.terms = list(reader)
            print(f"✅ Загружено {len(self.terms)} терминов из {self.csv_path}")
        except FileNotFoundError:
            print(f"❌ Файл {self.csv_path} не найден")
            self.terms = []
        except Exception as e:
            print(f"❌ Ошибка при загрузке CSV: {e}")
            self.terms = []
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Поиск терминов по запросу
        
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

