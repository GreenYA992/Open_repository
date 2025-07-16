import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv
import os

load_dotenv('C://Users//Green//OneDrive//Рабочий стол//Обучение//Python//New_Project_Code//ImprovedPython//DZdict//tmp.env')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.yandex.ru')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@example.com')

msg = MIMEText("Тестовое письмо из Python")
msg['Subject'] = 'Тест SMTP'
msg['From'] = SMTP_USERNAME
msg['To'] = "greenya992@gmail.com"

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
    print("✅ Письмо отправлено!")
except Exception as e:
    print(f"❌ Ошибка: {e}")
