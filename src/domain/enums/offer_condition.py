from enum import Enum


class OfferCondition(str, Enum):
    NEW = "new"
    USED = "used"
    REFURBISHED = "refurbished"
