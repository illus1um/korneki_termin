"""
Сервис для сбора и анализа статистики использования бота
"""
import asyncio
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter, defaultdict


class AnalyticsService:
    """Сервис для сбора аналитики (Singleton) с асинхронной записью"""
    
    _instance: Optional['AnalyticsService'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if AnalyticsService._initialized:
            return
        
        self.data_dir = Path('data')
        self.analytics_file = self.data_dir / 'analytics.csv'
        self.backups_dir = self.data_dir / 'backups'
        
        # Создаём директории если их нет
        self.data_dir.mkdir(exist_ok=True)
        self.backups_dir.mkdir(exist_ok=True)
        
        # Инициализируем файл аналитики
        self._ensure_analytics_file()
        
        # Асинхронная очередь для событий
        self._queue: Optional[asyncio.Queue] = None
        self._worker_task: Optional[asyncio.Task] = None
        self._running = False
        
        AnalyticsService._initialized = True
    
    def _ensure_analytics_file(self):
        """Создаёт файл аналитики с заголовками если его нет"""
        if not self.analytics_file.exists():
            with open(self.analytics_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'user_id', 'username', 'event_type', 
                    'lang', 'category', 'subcategory', 'query', 'results_count'
                ])
    
    async def start(self):
        """Запуск фонового воркера для записи событий"""
        if self._running:
            return
        
        self._queue = asyncio.Queue(maxsize=1000)  # Ограничение размера очереди
        self._running = True
        self._worker_task = asyncio.create_task(self._worker())
    
    async def stop(self):
        """Остановка фонового воркера"""
        self._running = False
        if self._queue:
            await self._queue.put(None)  # Сигнал остановки
        if self._worker_task:
            await self._worker_task
    
    async def _worker(self):
        """Фоновый воркер для записи событий в файл"""
        batch = []
        batch_size = 10  # Записываем батчами для эффективности
        batch_timeout = 1.0  # Максимальное время ожидания перед записью батча
        
        while self._running:
            try:
                # Ждём событие с таймаутом
                try:
                    event = await asyncio.wait_for(self._queue.get(), timeout=batch_timeout)
                except asyncio.TimeoutError:
                    # Таймаут - записываем накопленный батч если есть
                    if batch:
                        await self._write_batch(batch)
                        batch = []
                    continue
                
                # Если получили сигнал остановки (None)
                if event is None:
                    break
                
                batch.append(event)
                
                # Записываем батч если накопилось достаточно
                if len(batch) >= batch_size:
                    await self._write_batch(batch)
                    batch = []
            except Exception as e:
                print(f"[ERROR] Ошибка в воркере аналитики: {e}")
        
        # Записываем оставшиеся события перед остановкой
        if batch:
            await self._write_batch(batch)
    
    async def _write_batch(self, batch: List[Dict]):
        """Асинхронная запись батча событий в файл"""
        if not batch:
            return
        
        # Используем asyncio.to_thread для неблокирующей записи
        def write_to_file():
            try:
                with open(self.analytics_file, 'a', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    for event in batch:
                        writer.writerow([
                            event['timestamp'],
                            event['user_id'],
                            event['username'],
                            event['event_type'],
                            event['lang'],
                            event['category'],
                            event['subcategory'],
                            event['query'],
                            event['results_count']
                        ])
            except Exception as e:
                print(f"[ERROR] Ошибка при записи аналитики: {e}")
        
        await asyncio.to_thread(write_to_file)
    
    async def log_event(
        self,
        user_id: int,
        event_type: str,
        username: Optional[str] = None,
        lang: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        query: Optional[str] = None,
        results_count: int = 0
    ):
        """
        Асинхронное логирование события (неблокирующее)
        
        Args:
            user_id: ID пользователя
            event_type: Тип события (language_selected, category_selected, search, etc.)
            username: Имя пользователя (опционально)
            lang: Язык интерфейса
            category: Категория
            subcategory: Подкатегория
            query: Поисковый запрос
            results_count: Количество результатов
        """
        if not self._running or not self._queue:
            # Если воркер не запущен, запускаем его
            await self.start()
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'username': username or '',
            'event_type': event_type,
            'lang': lang or '',
            'category': category or '',
            'subcategory': subcategory or '',
            'query': query or '',
            'results_count': results_count
        }
        
        try:
            # Пытаемся добавить в очередь без блокировки
            self._queue.put_nowait(event)
        except asyncio.QueueFull:
            # Если очередь переполнена, просто логируем ошибку (не блокируем обработку)
            print(f"[WARNING] Очередь аналитики переполнена, событие пропущено")
    
    def get_stats(self, days: int = 7) -> Dict:
        """
        Получить статистику за последние N дней
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            Словарь со статистикой
        """
        if not self.analytics_file.exists():
            return self._empty_stats()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        events = []
        
        try:
            with open(self.analytics_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        event_time = datetime.fromisoformat(row['timestamp'])
                        if event_time >= cutoff_date:
                            events.append(row)
                    except:
                        continue
        except Exception as e:
            print(f"[ERROR] Ошибка при чтении аналитики: {e}")
            return self._empty_stats()
        
        if not events:
            return self._empty_stats()
        
        # Уникальные пользователи
        unique_users = set(int(e['user_id']) for e in events if e['user_id'].isdigit())
        
        # Статистика по языкам
        lang_counter = Counter(e['lang'] for e in events if e['lang'])
        
        # Статистика по категориям
        category_counter = Counter(e['category'] for e in events if e['category'] and e['event_type'] == 'category_selected')
        
        # Статистика по поисковым запросам
        search_events = [e for e in events if e['event_type'] == 'search']
        query_counter = Counter(e['query'].lower() for e in search_events if e['query'])
        
        # Успешные/неуспешные поиски
        successful_searches = sum(1 for e in search_events if int(e.get('results_count', 0)) > 0)
        failed_searches = len(search_events) - successful_searches
        
        # События сегодня
        today = datetime.now().date()
        today_events = [e for e in events if datetime.fromisoformat(e['timestamp']).date() == today]
        today_users = set(int(e['user_id']) for e in today_events if e['user_id'].isdigit())
        
        return {
            'period_days': days,
            'total_events': len(events),
            'unique_users': len(unique_users),
            'unique_users_today': len(today_users),
            'languages': dict(lang_counter),
            'top_categories': dict(category_counter.most_common(10)),
            'top_queries': dict(query_counter.most_common(10)),
            'search_stats': {
                'total': len(search_events),
                'successful': successful_searches,
                'failed': failed_searches,
                'success_rate': (successful_searches / len(search_events) * 100) if search_events else 0
            },
            'events_today': len(today_events)
        }
    
    def _empty_stats(self) -> Dict:
        """Возвращает пустую статистику"""
        return {
            'period_days': 0,
            'total_events': 0,
            'unique_users': 0,
            'unique_users_today': 0,
            'languages': {},
            'top_categories': {},
            'top_queries': {},
            'search_stats': {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0
            },
            'events_today': 0
        }
    
    def get_failed_queries(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """
        Получить запросы без результатов (что добавить в базу?)
        
        Args:
            days: Количество дней для анализа
            limit: Максимальное количество результатов
            
        Returns:
            Список словарей с запросами и количеством попыток
        """
        if not self.analytics_file.exists():
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        failed_queries = []
        
        try:
            with open(self.analytics_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        event_time = datetime.fromisoformat(row['timestamp'])
                        if (event_time >= cutoff_date and 
                            row['event_type'] == 'search' and 
                            int(row.get('results_count', 0)) == 0 and
                            row.get('query')):
                            failed_queries.append(row['query'].lower())
                    except:
                        continue
        except Exception as e:
            print(f"[ERROR] Ошибка при чтении аналитики: {e}")
            return []
        
        # Подсчитываем частоту
        query_counter = Counter(failed_queries)
        return [
            {'query': query, 'count': count}
            for query, count in query_counter.most_common(limit)
        ]
    
    def get_user_activity(self, days: int = 7) -> Dict:
        """
        Получить активность пользователей по дням
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            Словарь с активностью по дням
        """
        if not self.analytics_file.exists():
            return {}
        
        cutoff_date = datetime.now() - timedelta(days=days)
        daily_activity = defaultdict(int)
        
        try:
            with open(self.analytics_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        event_time = datetime.fromisoformat(row['timestamp'])
                        if event_time >= cutoff_date:
                            date_key = event_time.date().isoformat()
                            daily_activity[date_key] += 1
                    except:
                        continue
        except Exception as e:
            print(f"[ERROR] Ошибка при чтении аналитики: {e}")
            return {}
        
        return dict(daily_activity)
    
    def export_analytics(self, output_path: Optional[Path] = None) -> Path:
        """
        Экспорт аналитики в CSV
        
        Args:
            output_path: Путь для сохранения (если None - создаст автоматически)
            
        Returns:
            Путь к экспортированному файлу
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.data_dir / f'analytics_export_{timestamp}.csv'
        
        if self.analytics_file.exists():
            import shutil
            shutil.copy(self.analytics_file, output_path)
        
        return output_path

