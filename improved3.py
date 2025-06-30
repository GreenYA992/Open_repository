import asyncio as asy
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from io import BytesIO
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime
import json


class Model(ABC):
    @abstractmethod
    async def download_data(self, skip: int, cat: int) -> bytes:
        pass

    @abstractmethod
    def transform_to_dict(self, raw_data: bytes) -> Optional[Dict[str, Any]]:
        pass


class AsyncLoader(Model):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AsyncLoader, cls).__new__(cls)
            cls._instance.session = None
        return cls._instance

    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def download_data(self, skip: int, cat: int) -> bytes:
        if not isinstance(skip, int) or not isinstance(cat, int):
            raise TypeError('Категория и skip должны быть целыми числами')

        url = (f'https://analitika.woysa.club/images/panel/json/download/niches.php?'
               f'skip={skip}0&price_min=0&price_max=1060225&up_vy_min=0'
               f'&up_vy_max=108682515&up_vy_pr_min=0&up_vy_pr_max=2900&sum_min=1000'
               f'&sum_max=82432725&feedbacks_min=0&feedbacks_max=32767&trend=false'
               f'&sort=sum_sale&sort_dir=-1&id_cat={cat}')

        try:
            await self.init_session()
            async with self.session.get(url, timeout=30) as response:
                if response.status != 200:
                    raise ValueError(f'HTTP ошибка: {response.status}')
                content = await response.read()
                if not content:
                    raise ValueError('Пустой ответ от сервера')
                return content
        except aiohttp.ClientError as e:
            raise ValueError(f'Ошибка соединения: {str(e)}')
        except asy.TimeoutError:
            raise ValueError('Таймаут запроса')

    def transform_to_dict(self, raw_data: bytes) -> Optional[Dict[str, Any]]:
        try:
            excel_data = pd.read_excel(BytesIO(raw_data))
            if excel_data.empty:
                return None
            return {str(index): row.to_dict() for index, row in excel_data.iterrows()}
        except Exception as e:
            print(f'Ошибка преобразования данных: {str(e)}')
            return None

    async def save_to_json(self,
                           data: Dict[int, Dict[str, Any]],
                           directory: str = 'results',
                           filename: str = None) -> str:
        """
        Сохраняет данные в JSON-файл
        :param data: Словарь с данными для сохранения
        :param directory: Директория для сохранения (по умолчанию 'results')
        :param filename: Имя файла (если None, будет сгенерировано автоматически)
        :return: Путь к сохраненному файлу
        """
        try:
            # Создаем директорию, если она не существует
            Path(directory).mkdir(parents=True, exist_ok=True)
            # Генерируем имя файла, если не указано
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'categories_{timestamp}.json'
            filepath = Path(directory) / filename
            # Конвертируем данные в JSON-совместимый формат
            json_data = {
                str(cat): category_data
                for cat, category_data in data.items()
            }
            # Сохраняем в файл с красивым форматированием
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
            print(f'Данные успешно сохранены в {filepath}')
            return str(filepath)
        except Exception as e:
            raise ValueError(f'Ошибка при сохранении JSON: {str(e)}')


class ThreadedProcessor:
    def __init__(self, loader: AsyncLoader, max_workers: int = 10):
        self.loader = loader
        self.max_workers = max_workers

    async def _process_single_category(self, skip: int, cat: int) -> Optional[Dict[int, Dict[str, Any]]]:
        try:
            raw_data = await self.loader.download_data(skip, cat)
            with ThreadPoolExecutor(max_workers=1) as executor:
                data_dict = await asy.get_event_loop().run_in_executor(
                    executor, self.loader.transform_to_dict, raw_data
                )
                if data_dict:
                    return {cat: data_dict}
        except Exception as e:
            print(f'Ошибка обработки категории {cat}: {str(e)}')
        return None

    async def download_categories(self, categories: List[int], skip: int = 0, batch_size: int = 20) -> Dict[
        int, Dict[str, Any]]:
        if not categories:
            return {}
        # Разбиваем категории на пакеты
        batches = np.array_split(categories, max(1, len(categories) // batch_size))
        results = {}
        for batch in batches:
            if len(batch) == 0:
                continue
            # Создаем задачи для каждой категории в пакете
            tasks = [
                self._process_single_category(skip, int(cat))
                for cat in batch
            ]
            # Ожидаем завершения всех задач в пакете
            batch_results = await asy.gather(*tasks)
            # Собираем результаты
            for result in batch_results:
                if result:
                    results.update(result)
        return results


async def main():
    asy_loader = AsyncLoader()
    processor = ThreadedProcessor(asy_loader, max_workers=15)

    try:
        all_categories = list(range(100, 501))
        print('Запуск загрузки набора категорий...')
        final_result = await processor.download_categories(all_categories, batch_size=25)
        if not final_result:
            print('Основная загрузка не удалась - пустой результат.')
            return
        print(f'Успешно загружено {len(final_result)} категорий.')
        # Сохраняем результаты
        save_path = await asy_loader.save_to_json(
            final_result,
            directory='C://Users//Green//OneDrive//Рабочий стол//Обучение//Python//New_Project_Code//ImprovedPython'
        )
        print(f'Данные сохранены в: {save_path}')
        # Выводим пример данных для проверки
        sample_cat = next(iter(final_result))
        print(f'\nПример данных для категории {sample_cat}:')
        print(f'Количество записей: {len(final_result[sample_cat])}')
        print(f'Первая запись: {list(final_result[sample_cat].values())[0]}')

    except Exception as e:
        print(f'Критическая ошибка: {str(e)}')
    finally:
        await asy_loader.close_session()


if __name__ == '__main__':
    asy.run(main())
