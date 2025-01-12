# **4WritersAPI**

### **Описание**
4WritersAPI — это API для взаимодействия с сайтом [4writers.net](https://www.4writers.net). Этот инструмент позволяет автоматизировать работу с сайтом, включая авторизацию и получение доступных заказов.

---

### **Функционал**
1. **Авторизация**
   - Выполняется с использованием логина и пароля.
   - Сохраняет сессию для выполнения последующих запросов.

2. **Получение заказов**
   - API парсит доступные заказы с сайта и возвращает их в структурированном виде.
   - Поддерживаемая информация:
     - ID заказа.
     - Название.
     - Тема.
     - Дедлайн.
     - Время до выполнения.
     - Тип работы.
     - Уровень академической сложности.
     - Стиль оформления.
     - Язык.
     - Количество страниц.
     - Количество источников.
     - Оплата (зарплата, бонус, общая сумма).

---

### **Установка**
1. Убедитесь, что у вас установлен **Python 3.8** или выше.
2. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/your-repo/4writersAPI.git
   cd 4writersAPI

Установите зависимости:
```bash
pip install -r requirements.txt
```
### Настройка
Создайте файл .env в корне проекта и добавьте ваши учетные данные:
```env
LOGIN=your_login
PASSWORD=your_password
```
### Использование
Пример использования API для авторизации и получения заказов:

```python
import asyncio
from src.api.api import API
from envparse import env

# Загрузка данных из .env файла
env.read_envfile(".env")
LOGIN = env.str("LOGIN")
PASSWORD = env.str("PASSWORD")

# Инициализация API
api = API(login=LOGIN, password=PASSWORD)

async def main():
    # Авторизация
    await api.login()
    
    # Получение заказов
    orders = await api.get_orders()
    
    if not orders:
        print("No orders found.")
    else:
        for order in orders:
            print("=" * 40)
            print(f"Order ID: {order.order_id}")
            print(f"Title: {order.title}")
            print(f"Subject: {order.subject}")
            print(f"Deadline: {order.deadline}")
            print(f"Remaining: {order.remaining}")
            print(f"Order Type: {order.order_type}")
            print(f"Academic Level: {order.academic_level}")
            print(f"Style: {order.style}")
            print(f"Language: {order.language}")
            print(f"Pages: {order.pages}")
            print(f"Sources: {order.sources}")
            print(f"Salary: ${order.salary:.2f}")
            print(f"Bonus: ${order.bonus:.2f}")
            print(f"Total: ${order.total:.2f}")
            print("=" * 40)

asyncio.run(main())
```