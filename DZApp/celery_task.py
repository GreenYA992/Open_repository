from celery import Celery
from ImprovedPython.DZdict.connect import async_session_factory
from sqlalchemy import select, func
from datetime import datetime, timedelta
from ImprovedPython.DZdict.tables import Supplier, Product, Order
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv


load_dotenv('C://Users//Green//OneDrive/'
            '/Рабочий стол//Обучение//Python/'
            '/New_Project_Code//ImprovedPython/'
            '/DZdict//tmp.env')

app = Celery('ImprovedPython.DZdict.celery_task', broker='redis://localhost:6379/0')

SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.yandex.ru')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@example.com')


@app.task(bind=True)
def generate_seller_statistics(self, seller_id: int, email: str):
    # Запускаем асинхронный код в event loop
    import asyncio
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_async_generate_stats(seller_id, email))

async def _async_generate_stats(seller_id: int, email: str):
    async with async_session_factory() as session:
        # 1. Получаем основную информацию о продавце
        seller_result = await session.execute(select(Supplier).where(Supplier.ID == seller_id))
        seller = seller_result.scalars().first()

        if not seller:
            return {"status": "error", "message": "Seller not found"}

        # 2. Собираем статистику
        # Количество товаров у продавца
        products_count = await session.execute(
            select(func.count(Product.ID)).where(Product.SupplierID == seller_id))
        products_count = products_count.scalar()

        # Общее количество продаж
        total_sales = await session.execute(
            select(func.sum(Order.Quantity)).where(Order.SupplierID == seller_id))
        total_sales = total_sales.scalar() or 0

        # Количество отгрузок за последний месяц
        one_month_ago = datetime.now() - timedelta(days=30)
        shipments_count = await session.execute(
            select(func.count(Order.ID)).where(
                Order.SupplierID == seller_id,
                Order.OrderDate >= one_month_ago
            ))
        shipments_count = shipments_count.scalar()

        # 3. Формируем отчет
        report = f"""
        Статистика по продавцу: {seller.Name}
        Бренд: {seller.Brand or 'Не указан'}

        Количество товаров: {products_count}
        Общее количество продаж: {total_sales}
        Количество отгрузок за последний месяц: {shipments_count}
        """

        # 4. Отправляем email
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_FROM
            msg['To'] = email
            msg['Subject'] = f"Статистика по продавцу {seller.Name}"

            msg.attach(MIMEText(report, 'plain'))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)

            return {"status": "success", "message": "Report sent successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
