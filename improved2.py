import asyncio as asy, pandas as pd, numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from io import BytesIO
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime
import json

class Model(ABC):
    @abstractmethod
    def download_data(self, skip, cat) -> Any:
        """Абстрактный метод для получения данных с веб-сайта по категориям"""
        pass

    @abstractmethod
    def transform_to_dict(self, raw_data: Any) -> Dict[str, Any]:
        """Абстрактный метод для преобразования данных в словарь"""
        pass


class AsyncLoader(Model):
    _instance = None
    def __new__(cls):
        """Реализация Singleton"""
        if cls._instance is None:
            cls._instance = super(AsyncLoader, cls).__new__(cls)
            cls._instance.session = None
        return cls._instance

    async def init_session(self):
        """Инициализация aiohttp сессии"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        """Закрытие aiohttp сессии"""
        if self.session:
            await self.session.close()
            self.session = None

    async def download_data(self, skip: int, cat: int) -> bytes:
        """Загрузка данных с woysa.club"""
        if not isinstance(skip, int) or not isinstance(cat, int):
            raise TypeError('Все категории должны быть целыми числами')

        url = (f'https://analitika.woysa.club/images/panel/json/download/niches.php?'
               f'skip={skip}0&price_min=0&price_max=1060225&up_vy_min=0'
               f'&up_vy_max=108682515&up_vy_pr_min=0&up_vy_pr_max=2900&sum_min=1000'
               f'&sum_max=82432725&feedbacks_min=0&feedbacks_max=32767&trend=false'
               f'&sort=sum_sale&sort_dir=-1&id_cat={cat}')
        try:
            await self.init_session()
            async with self.session.get(url, timeout=10) as response:
                if response.status != 200:
                    raise ValueError(f'Ошибка сервера: {response.status}')
                return await response.read()
        except aiohttp.ClientError as e:
            raise ValueError(f'Ошибка при выполнении запроса: {str(e)}')

    def transform_to_dict(self, raw_data: bytes) -> Dict[str, Any]:
        """Конвертация XLSX-файла в словарь с помощью pandas"""
        try:
            # Чтение XLSX-файла
            excel_data = pd.read_excel(BytesIO(raw_data))
            # Преобразование в словарь с ключами - индексами строк
            return ({str(index): row.to_dict()
                for index, row in excel_data.iterrows()} if len(excel_data) > 0 else None)
        except Exception as e:
            raise ValueError(f'Ошибка при конвертации XLSX в словарь: {str(e)}')

    async def download_multiple_categories(self, categories:
    List[int], skip: int = 0, batch_size: int = 10) -> Dict[int, Dict[str, Any]]:
        """Многопоточная загрузка данных по категориям"""
        if not categories:
            return {}
        # Разбиваем категории на пакеты
        batches = np.array_split(categories, max(1, len(categories) // batch_size))
        processed_data = {}
        # Создаем задачи для каждой категории
        for batch in batches:
            if len(batch) == 0:
                continue
            tasks = [asy.create_task(self.download_data(skip, int(cat))) for cat in batch]
            results = await asy.gather(*tasks, return_exceptions=True)
            # Параллельная обработка результатов пакета
            with ThreadPoolExecutor() as executor:
                for cat, result in zip(batch, results): # categories
                    if isinstance(result, Exception):
                        print(f'Ошибка для категории {cat}: {str(result)}')
                        continue
                    # Используем многопоточность
                    future = executor.submit(self.transform_to_dict, result)
                    data_dict = future.result()
                    if data_dict is not None:  # Пропускаем None (пустые категории)
                        processed_data[int(cat)] = data_dict
                    else:
                        print(f'Категория {cat} пропущена (0 записей)')
        return processed_data

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
            # Сохраняем в файл
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
            print(f'Данные успешно сохранены в {filepath}')
            return str(filepath)
        except Exception as e:
            raise ValueError(f'Ошибка при сохранении JSON: {str(e)}')

async def main():
    asy_loader = AsyncLoader()
    try:
        # categories = [100, 200, 300, 400, 500]
        # res = await asy_loader.download_multiple_categories(categories)
        categories = list(range(100, 501))
        res = await asy_loader.download_multiple_categories(categories, batch_size=20)
        await asy_loader.save_to_json(res, directory='C://Users//Green//OneDrive//Рабочий стол//Обучение//Python//New_Project_Code//ImprovedPython')
        for cat, data in res.items():
            print(f'\nКатегория {cat}:')
            print(f'Первая запись: {data.get('0', 'Словарь пуст')}')
            print(f'Всего записей: {len(data)}')
    finally:
        await asy_loader.close_session()

if __name__ == '__main__':
    asy.run(main())
