from enum import Enum


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"
    KZT = "KZT"
    KGZ = "KGZ"
