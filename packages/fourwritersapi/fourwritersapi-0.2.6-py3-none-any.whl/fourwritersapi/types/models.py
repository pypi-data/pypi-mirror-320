from dataclasses import dataclass


@dataclass
class Order:
    title: str
    subject: str
    order_id: str
    deadline: str
    remaining: str
    order_type: str
    academic_level: str
    style: str
    language: str
    pages: int
    sources: int
    salary: float
    bonus: float
    total: float
