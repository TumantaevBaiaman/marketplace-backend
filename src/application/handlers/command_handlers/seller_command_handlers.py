from src.application.commands.seller_commands import CreateSellerCommand, UpdateSellerCommand
from src.application.dto.seller_dto import AdminSellerResponseDTO
from src.domain.entities.seller import Seller
from src.domain.exceptions.domain_exceptions import EntityNotFound
from src.domain.repositories.seller_repository import SellerRepository


def _to_dto(seller: Seller) -> AdminSellerResponseDTO:
    return AdminSellerResponseDTO(
        id=seller.id,
        name=seller.name,
        description=seller.description,
        email=seller.email,
        phone=seller.phone,
        website=seller.website,
        country=seller.country,
        rating=seller.rating,
        review_count=seller.review_count,
        is_verified=seller.is_verified,
    )


class CreateSellerHandler:
    def __init__(self, seller_repo: SellerRepository):
        self._sellers = seller_repo

    async def handle(self, command: CreateSellerCommand) -> AdminSellerResponseDTO:
        seller = Seller(
            name=command.name,
            description=command.description,
            email=command.email,
            phone=command.phone,
            website=command.website,
            country=command.country,
            rating=command.rating,
            is_verified=command.is_verified,
        )
        await self._sellers.save(seller)
        return _to_dto(seller)


class UpdateSellerHandler:
    def __init__(self, seller_repo: SellerRepository):
        self._sellers = seller_repo

    async def handle(self, command: UpdateSellerCommand) -> AdminSellerResponseDTO:
        seller = await self._sellers.get_by_id(command.seller_id)
        if not seller:
            raise EntityNotFound("Seller not found")
        if command.name is not None:
            seller.name = command.name
        if command.description is not None:
            seller.description = command.description
        if command.email is not None:
            seller.email = command.email
        if command.phone is not None:
            seller.phone = command.phone
        if command.website is not None:
            seller.website = command.website
        if command.country is not None:
            seller.country = command.country
        if command.rating is not None:
            seller.rating = command.rating
        if command.is_verified is not None:
            seller.is_verified = command.is_verified
        await self._sellers.save(seller)
        return _to_dto(seller)
