from src.application.dto.offer_dto import AdminOfferResponseDTO
from src.application.dto.product_dto import MoneyDTO
from src.application.queries.offer_queries import GetOffersByProductQuery
from src.domain.repositories.offer_repository import OfferRepository
from src.domain.repositories.seller_repository import SellerRepository


class GetOffersByProductHandler:
    def __init__(self, offer_repo: OfferRepository, seller_repo: SellerRepository | None = None):
        self._offers = offer_repo
        self._sellers = seller_repo

    async def handle(self, query: GetOffersByProductQuery) -> list[AdminOfferResponseDTO]:
        offers = await self._offers.get_by_product(query.product_id)
        result = []
        for o in offers:
            seller_name = None
            if self._sellers:
                seller = await self._sellers.get_by_id(o.seller_id)
                seller_name = seller.name if seller else None
            result.append(
                AdminOfferResponseDTO(
                    id=o.id,
                    product_id=o.product_id,
                    seller_id=o.seller_id,
                    seller_name=seller_name,
                    price=MoneyDTO(amount=o.price_amount, currency=o.price_currency),
                    delivery_date=o.delivery_date,
                    condition=getattr(o, "condition", "new") or "new",
                    quantity=getattr(o, "quantity", 1) or 1,
                    is_available=getattr(o, "is_available", True)
                    if getattr(o, "is_available", True) is not None
                    else True,
                    delivery_days_min=getattr(o, "delivery_days_min", None),
                    delivery_days_max=getattr(o, "delivery_days_max", None),
                )
            )
        return result
