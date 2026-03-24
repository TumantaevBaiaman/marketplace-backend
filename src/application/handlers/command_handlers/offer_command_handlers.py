from src.application.commands.offer_commands import (
    CreateOfferCommand,
    DeleteOfferCommand,
    UpdateOfferCommand,
)
from src.application.dto.offer_dto import AdminOfferResponseDTO
from src.application.dto.product_dto import MoneyDTO
from src.domain.entities.offer import Offer
from src.domain.exceptions.domain_exceptions import EntityNotFound
from src.domain.repositories.offer_repository import OfferRepository


def _to_dto(offer: Offer) -> AdminOfferResponseDTO:
    return AdminOfferResponseDTO(
        id=offer.id,
        product_id=offer.product_id,
        seller_id=offer.seller_id,
        price=MoneyDTO(amount=offer.price_amount, currency=offer.price_currency),
        delivery_date=offer.delivery_date,
        condition=offer.condition,
        quantity=offer.quantity,
        is_available=offer.is_available,
        delivery_days_min=offer.delivery_days_min,
        delivery_days_max=offer.delivery_days_max,
    )


class CreateOfferHandler:
    def __init__(self, offer_repo: OfferRepository):
        self._offers = offer_repo

    async def handle(self, command: CreateOfferCommand) -> AdminOfferResponseDTO:
        offer = Offer(
            product_id=command.product_id,
            seller_id=command.seller_id,
            price_amount=command.price_amount,
            price_currency=command.price_currency,
            delivery_date=command.delivery_date,
            condition=command.condition,
            quantity=command.quantity,
            is_available=command.is_available,
            delivery_days_min=command.delivery_days_min,
            delivery_days_max=command.delivery_days_max,
        )
        await self._offers.save(offer)
        return _to_dto(offer)


class UpdateOfferHandler:
    def __init__(self, offer_repo: OfferRepository):
        self._offers = offer_repo

    async def handle(self, command: UpdateOfferCommand) -> AdminOfferResponseDTO:
        offer = await self._offers.get_by_id(command.offer_id)
        if not offer:
            raise EntityNotFound("Offer not found")
        if command.seller_id is not None:
            offer.seller_id = command.seller_id
        if command.price_amount is not None:
            offer.price_amount = command.price_amount
        if command.price_currency is not None:
            offer.price_currency = command.price_currency
        if command.delivery_date is not None:
            offer.delivery_date = command.delivery_date
        if command.condition is not None:
            offer.condition = command.condition
        if command.quantity is not None:
            offer.quantity = command.quantity
        if command.is_available is not None:
            offer.is_available = command.is_available
        if command.delivery_days_min is not None:
            offer.delivery_days_min = command.delivery_days_min
        if command.delivery_days_max is not None:
            offer.delivery_days_max = command.delivery_days_max
        await self._offers.save(offer)
        return _to_dto(offer)


class DeleteOfferHandler:
    def __init__(self, offer_repo: OfferRepository):
        self._offers = offer_repo

    async def handle(self, command: DeleteOfferCommand) -> None:
        offer = await self._offers.get_by_id(command.offer_id)
        if not offer:
            raise EntityNotFound("Offer not found")
        await self._offers.delete(command.offer_id)
