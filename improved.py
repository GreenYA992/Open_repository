import requests
from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd
from io import BytesIO

class Model(ABC):
    @abstractmethod
    def download_data(self, skip, cat) -> Any:
        """Абстрактный метод для получения данных с веб-сайта по категориям"""
        pass

    @abstractmethod
    def transform_to_dict(self, raw_data: Any) -> Dict[str, Any]:
        """Абстрактный метод для преобразования данных в словарь"""
        pass


class Loader(Model):
    _instance = None
    def __new__(cls):
        """Реализация Singleton"""
        if cls._instance is None:
            cls._instance = super(Loader, cls).__new__(cls)
        return cls._instance

    def download_data(self, skip, cat) -> requests.Response:
        """Загрузка данных с woysa.club"""
        if not cat and not skip:
            raise ValueError('Списки не могут быть пустыми')
        if not isinstance(skip or cat, int):
            raise TypeError('Все категории должны быть целыми числами')

        url = (f'https://analitika.woysa.club/images/panel/json/download/niches.php?'
               f'skip={skip}0&price_min=0&price_max=1060225&up_vy_min=0'
               f'&up_vy_max=108682515&up_vy_pr_min=0&up_vy_pr_max=2900&sum_min=1000'
               f'&sum_max=82432725&feedbacks_min=0&feedbacks_max=32767&trend=false'
               f'&sort=sum_sale&sort_dir=-1&id_cat={cat}')
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                raise ValueError(f'Ошибка сервера: {response.status_code}')
            return response
        except requests.RequestException as e:
            raise ValueError(f'Ошибка при выполнении запроса: {str(e)}')

    def transform_to_dict(self, raw_data: requests.Response) -> Dict[str, Any]:
        """Конвертация XLSX-файла в словарь с помощью pandas"""
        try:
            # Чтение XLSX-файла из бинарных данных ответа
            excel_data = pd.read_excel(BytesIO(raw_data.content))
            # Преобразование в словарь с ключами - индексами строк
            result_dict = {str(index): row.to_dict()
                for index, row in excel_data.iterrows()}
            return result_dict
        except Exception as e:
            raise ValueError(f'Ошибка при конвертации XLSX в словарь: {str(e)}')

if __name__ == '__main__':
    loader = Loader()
    data = loader.download_data(100, 10_000)
    print('Загруженные данные:', data.status_code)
    if data.status_code == 200:
        print(f"Первая запись из словаря: {loader.transform_to_dict(data).get('0', 'Словарь пуст')}")
        print(f"Всего записей: {len(loader.transform_to_dict(data))}")
