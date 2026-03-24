from src.application.dto.seller_dto import AdminSellerResponseDTO
from src.application.queries.seller_queries import ListSellersQuery
from src.domain.repositories.seller_repository import SellerRepository


class ListSellersHandler:
    def __init__(self, seller_repo: SellerRepository):
        self._sellers = seller_repo

    async def handle(self, query: ListSellersQuery) -> list[AdminSellerResponseDTO]:
        sellers = await self._sellers.get_all()
        return [
            AdminSellerResponseDTO(
                id=s.id,
                name=s.name,
                description=s.description,
                email=s.email,
                phone=s.phone,
                website=s.website,
                country=s.country,
                rating=s.rating,
                review_count=s.review_count,
                is_verified=s.is_verified,
            )
            for s in sellers
        ]
