from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, text, Numeric, inspect
import datetime
from typing import List, Optional


class BaseTable(DeclarativeBase):
    __abstract__ = True

def create_table_if_not_exists(engine):
    """Создает таблицы, если они не существуют в базе данных"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    required_tables = ["Suppliers", "Products", "Orders"]
    missing_tables = [table for table in required_tables if table not in existing_tables]
    if missing_tables:
        print(f"Создаем отсутствующие таблицы: {', '.join(missing_tables)}")
        BaseTable.metadata.create_all(engine)
    else:
        print("Все таблицы уже существуют в базе данных")


class Supplier(BaseTable):
    __tablename__ = "Suppliers"

    ID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Name: Mapped[str] = mapped_column(String(100))
    Brand: Mapped[Optional[str]] = mapped_column(String(100))  # Бренд
    Contact: Mapped[Optional[str]] = mapped_column(String(100))  # Контактные данные
    CreatedOn: Mapped[datetime.datetime] = mapped_column(server_default=text("now()"))
    UpdatedAt: Mapped[datetime.datetime] = (
        mapped_column(server_default=text('now()'), onupdate=datetime.datetime.now()))

    products: Mapped[List["Product"]] = relationship("Product", back_populates="supplier")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="supplier")


class Product(BaseTable):
    __tablename__ = "Products"

    ID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    SKU: Mapped[int] = mapped_column(unique=True)  # Артикул
    Name: Mapped[str] = mapped_column(String(255))
    Price: Mapped[float] = mapped_column(Numeric(10, 2))
    Category: Mapped[str] = mapped_column(String(100))  # Основная категория
    SupplierID: Mapped[int] = mapped_column(ForeignKey("Suppliers.ID"))
    Stock: Mapped[int] = mapped_column()  # Остатки на складе
    ReviewsCount: Mapped[int] = mapped_column()  # Количество отзывов
    CreatedOn: Mapped[datetime.datetime] = mapped_column(server_default=text("now()"))
    UpdatedAt: Mapped[datetime.datetime] = (
        mapped_column(server_default=text('now()'), onupdate=datetime.datetime.now()))

    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="products")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="product")


class Order(BaseTable):
    __tablename__ = "Orders"

    ID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ProductID: Mapped[int] = mapped_column(ForeignKey("Products.ID"))
    SupplierID: Mapped[int] = mapped_column(ForeignKey("Suppliers.ID"))
    Quantity: Mapped[int]  # Количество заказов (из ваших данных)
    DaysOnSale: Mapped[int]  # Дней в продаже
    DaysWithSales: Mapped[int]  # Дней с продажами
    FBOTurnover: Mapped[float]  # Оборот FBO
    FBSTurnover: Mapped[float]  # Оборот FBS
    LostProfit: Mapped[float]  # Упущенная выгода
    LostProfitPercent: Mapped[float]  # Упущенная выгода в %
    SearchQueries: Mapped[int]  # Поисковых запросов
    OrderDate: Mapped[datetime.datetime] = mapped_column(server_default=text("now()"))

    product: Mapped["Product"] = relationship("Product", back_populates="orders")
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="orders")


class ProductODT:
    def __init__(self, product: Product):
        self.ID = product.ID
        self.Name = product.Name
        self.SKU = product.SKU
        self.Price = product.Price
        self.Category = product.Category
        self.Stock = product.Stock
        self.ReviewsCount = product.ReviewsCount
        self.Supplier = {
            'Name': product.supplier.Name,
            'Brand': product.supplier.Brand
        }

        # Агрегируем данные по заказам
        self.OrdersStats = {
            'TotalOrders': sum(order.Quantity for order in product.orders),
            'DaysOnSale': max(order.DaysOnSale for order in product.orders) if product.orders else 0,
            'DaysWithSales': max(order.DaysWithSales for order in product.orders) if product.orders else 0,
            'FBOTurnover': sum(order.FBOTurnover for order in product.orders),
            'FBSTurnover': sum(order.FBSTurnover for order in product.orders),
            'LostProfit': sum(order.LostProfit for order in product.orders),
            'LostProfitPercent': sum(order.LostProfitPercent for order in product.orders) / len(
                product.orders) if product.orders else 0,
            'SearchQueries': sum(order.SearchQueries for order in product.orders)
        }

    def display(self):
        print(f"ID: {self.ID}")
        print(f"Название: {self.Name}")
        print(f"SKU: {self.SKU}")
        print(f"Цена: {self.Price}")
        print(f"Категория: {self.Category}")
        print(f"Остатки: {self.Stock}")
        print(f"Отзывы: {self.ReviewsCount}")
        print("\nПоставщик:")
        print(f"  Название: {self.Supplier['Name']}")
        print(f"  Бренд: {self.Supplier['Brand']}")
        print("\nСтатистика заказов:")
        for key, value in self.OrdersStats.items():
            print(f"  {key}: {value}")
        print("=" * 50)
