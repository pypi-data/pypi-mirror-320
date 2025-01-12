import logging
from typing import List, Optional
from ..client.aiohttp import AiohttpClient
from ..types.models import Order
from ..const import Get, Post, USER_AGENT

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class API:
    def __init__(self, login: str = None, password: str = None, session: str = None):
        self.__login: str = login
        self.__password: str = password

        self.__session: str = None
        self.http_client: AiohttpClient = AiohttpClient()

    async def login(self) -> None:
        """Авторизация через login и password и сохранение sessionid."""
        if not self.__login or not self.__password:
            raise ValueError("Login and password are required for authentication.")

        response = await self.http_client.request_raw(
            url=Post.LOGIN,
            method="POST",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0",
                "Referer": Post.LOGIN,
            },
            data={"login": self.__login, "password": self.__password},
        )
        self.__session = response.cookies.get("session").output("session").split("=")[1]

    async def get_orders(self) -> Optional[List[Order]]:
        """Получает и парсит заказы, возвращая их в виде списка объектов Order или None, если заказов нет."""
        response = await self.http_client.request_raw(
            url=Get.ORDERS,
            method="GET",
            headers={
                "User-Agent": USER_AGENT,
                "Referer": Get.ORDERS,
                "Cookie": f"session={self.__session}",
            },
        )
        # print(self.__session)
        # print(await response.text())
        if response.status != 200:
            logger.error(f"Failed to fetch orders: {response.status}")
            return None

        html_content = await response.text()
        soup = BeautifulSoup(html_content, "html.parser")

        # Ищем все заказы
        order_items = soup.find_all("div", class_="order-item")
        if not order_items:
            logger.info("No orders found.")
            return []

        # Поля и их извлечение из HTML
        field_mapping = {
            "title": lambda order: order.find("div", class_="order_title").text.strip(),
            "subject": lambda order: order.find("div", class_="order_subject").text.strip(),
            "order_id": lambda order: order.find("div", class_="order_id").find("span", class_="value").text.strip(),
            "deadline": lambda order: order.find("div", class_="deadline").find("span", class_="value").text.strip(),
            "remaining": lambda order: order.find("div", class_="remaining").text.strip(),
            "order_type": lambda order: order.find("div", class_="label_cell", text="Order type").find_next_sibling("div").text.strip(),
            "academic_level": lambda order: order.find("div", class_="label_cell", text="Academic level").find_next_sibling("div").text.strip(),
            "style": lambda order: order.find("div", class_="label_cell", text="Style").find_next_sibling("div").text.strip(),
            "language": lambda order: order.find("div", class_="label_cell", text="Language").find_next_sibling("div").text.strip(),
            "pages": lambda order: int(order.find("div", class_="label_cell", text="Pages").find_next_sibling("div").text.strip()),
            "sources": lambda order: int(order.find("div", class_="label_cell", text="Sources").find_next_sibling("div").text.strip()),
            "salary": lambda order: float(order.find("div", class_="label_cell", text="Salary").find_next_sibling("div").text.strip().replace("$", "")),
            "bonus": lambda order: float(order.find("div", class_="label_cell", text="Bonus").find_next_sibling("div").text.strip().replace("$", "")),
            "total": lambda order: float(order.find("div", class_="label_cell", text="Total").find_next_sibling("div").text.strip().replace("$", "")),
        }

        # Создаём объекты Order
        orders = []
        for order_html in order_items:
            try:
                order_obj = Order(
                    title=field_mapping["title"](order_html),
                    subject=field_mapping["subject"](order_html),
                    order_id=field_mapping["order_id"](order_html),
                    deadline=field_mapping["deadline"](order_html),
                    remaining=field_mapping["remaining"](order_html),
                    order_type=field_mapping["order_type"](order_html),
                    academic_level=field_mapping["academic_level"](order_html),
                    style=field_mapping["style"](order_html),
                    language=field_mapping["language"](order_html),
                    pages=field_mapping["pages"](order_html),
                    sources=field_mapping["sources"](order_html),
                    salary=field_mapping["salary"](order_html),
                    bonus=field_mapping["bonus"](order_html),
                    total=field_mapping["total"](order_html),
                )
            except Exception as e:
                logger.warning(f"Error creating Order object: {e}")
                continue  # Skip this order if any field fails to extract
            for field, extractor in field_mapping.items():
                try:
                    setattr(order_obj, field, extractor(order_html))
                except (AttributeError, ValueError) as e:
                    logger.warning(f"Error extracting field {field}: {e}")
                    setattr(order_obj, field, None)  # Устанавливаем None, если ошибка
            orders.append(order_obj)

        return orders
