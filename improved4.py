from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, Session
from typing import Annotated, Any
import datetime

"""
===========================================
Connect to DB
===========================================
"""

class Connection:
    def __init__(self, sql_type, user, password, server, port=None, **args) -> None:
        self.sql_type = sql_type
        self.user = user
        self.password = password
        self.server = server
        self.port = port
        self.args = args
    @property
    def engine(self):
        if self.sql_type == 'MSSQL':
            return (f'mssql+pymssql://{self.user}:{self.password}'
                    f'@{self.server}/{self.args['db_name']}')
        if self.sql_type == 'PostgresSQL':
            return (f'postgresql://{self.user}:{self.password}'
                    f'@{self.server}:{str(self.port)}/{self.args['db_name']}')
        print('Соединение не поддерживается')
        return None
    @property
    def async_engine(self):
        if self.sql_type == 'MSSQL':
            return (f'mssql+aioodbc://{self.user}:'
                    f'{self.password}@{self.server}/{self.args['db_name']}')
        if self.sql_type == 'PostgresSQL':
            return (f'postgresql+asyncpg://{self.user}:'
                    f'{self.password}@{self.server}:{str(self.port)}/{self.args['db_name']}')
        print('Соединение не поддерживается')
        return None

class SessionBuilder:
    def __init__(self, connection: Connection):
        self.engine = create_engine(connection.engine)
        self.async_engine = create_async_engine(connection.async_engine)
    def build(self) -> sessionmaker:
        return sessionmaker(bind = self.engine)
    def async_build(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind = self.async_engine, class_ = AsyncSession, expire_on_commit = False)

"""
===========================================
Create Tables
===========================================
"""

class BaseTable(DeclarativeBase):
    __abstract__ = True # Указываем что это шаблон и не будет сохранен в БД

    type_annotation_map = {
        'IID': Annotated[int, mapped_column(primary_key=True, autoincrement=True)],
        'CreatedUpdated': Annotated[datetime.datetime,
        mapped_column(server_default=text('now()'), onupdate=datetime.datetime.now)],
        'CreatedOnly': Annotated[datetime.datetime, mapped_column(server_default=text('now()'))]}

    def __init__(self, **kwargs: Any) -> None:
        # Получаем все колонки таблицы
        columns = self.__table__.c.keys()  # или inspect(self.__class__).columns.keys()
        # Заполняем только те поля, которые есть в таблице
        for key, value in kwargs.items():
            if key in columns:
                setattr(self, key, value)

class Orders(BaseTable):
    __tablename__ = 'Заказы'
    ID: Mapped[BaseTable.type_annotation_map['IID']]
    Product_Name: Mapped[str]
    Cost: Mapped[int]
    Order_Date: Mapped[datetime.date]
    CreatedOn: Mapped[BaseTable.type_annotation_map['CreatedOnly']]
    UpdatedAt: Mapped[BaseTable.type_annotation_map['CreatedUpdated']]

class Vendors(BaseTable):
    __tablename__ = 'Поставщики'
    ID: Mapped[BaseTable.type_annotation_map['IID']]
    Vendor_Name: Mapped[str]
    Product_Name: Mapped[str]
    Cost: Mapped[int]
    CreatedOn: Mapped[BaseTable.type_annotation_map['CreatedOnly']]
    UpdatedAt: Mapped[BaseTable.type_annotation_map['CreatedUpdated']]

class Products(BaseTable):
    __tablename__ = 'Товары'
    ID: Mapped[BaseTable.type_annotation_map['IID']]
    Product_Name: Mapped[str]
    Vendor_Name: Mapped[str]
    Cost: Mapped[int]
    CreatedOn: Mapped[BaseTable.type_annotation_map['CreatedOnly']]
    UpdatedAt: Mapped[BaseTable.type_annotation_map['CreatedUpdated']]

"""
===========================================
Create Tables
===========================================
"""

"""Создаем соединение"""
connection = Connection(
        server='localhost',
        port=5432,
        user='postgres',
        password='password',
        db_name='Project',
        sql_type='PostgresSQL')
builder = SessionBuilder(connection)
"""Создаем таблицы"""
BaseTable.metadata.create_all(builder.engine)
"""Создаем сессию, для внесения данных"""
SessionFactory = builder.build()
with SessionFactory() as s:
    try:
        with builder.engine.connect() as conn:
            print("Подключение к базе данных успешно!")
    except Exception as e:
        print(f"Ошибка подключения: {e}")

    try:
        new_order = Orders(
            Product_Name="Телефон",
            Cost=30000,
            Order_Date=datetime.date(2023, 7, 1)
        )
        s.add(new_order)
        s.commit()
        print("Данные успешно добавлены!")
        #print(BaseTable.metadata.tables.keys())
    except Exception as e:
        s.rollback()
        print(f"Ошибка при добавлении данных: {e}")

"""
# Для удаления таблиц
(BaseTable.metadata.drop_all(builder.engine,
                             tables=[Orders.__table__, Vendors.__table__, Products.__table__]))
"""
