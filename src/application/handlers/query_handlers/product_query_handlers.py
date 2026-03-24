import uuid

from src.application.dto.product_dto import (
    AdminProductResponseDTO,
    MoneyDTO,
    OfferDTO,
    ProductAttributeDTO,
    ProductDetailsDTO,
    ProductListItemDTO,
    ProductListResponseDTO,
    SellerDTO,
)
from src.application.queries.product_queries import (
    AdminGetProductQuery,
    AdminListProductsQuery,
    GetPublicProductDetailsQuery,
    ListPublicProductsQuery,
)
from src.domain.exceptions.domain_exceptions import EntityNotFound
from src.domain.repositories.offer_repository import OfferRepository
from src.domain.repositories.product_attribute_repository import ProductAttributeRepository
from src.domain.repositories.product_repository import ProductRepository
from src.domain.repositories.seller_repository import SellerRepository
from src.domain.services.image_service import IImageService


class ListPublicProductsHandler:
    def __init__(
        self,
        product_repo: ProductRepository,
        offer_repo: OfferRepository,
        image_service: IImageService | None = None,
    ):
        self._products = product_repo
        self._offers = offer_repo
        self._image_service = image_service

    async def handle(self, query: ListPublicProductsQuery) -> ProductListResponseDTO:
        cursor_uuid = uuid.UUID(query.cursor) if query.cursor else None
        products, next_cursor = await self._products.get_list(
            query.limit, cursor_uuid, in_stock=query.in_stock, sort=query.sort
        )
        product_ids = [p.id for p in products]
        ratings = await self._products.get_ratings(product_ids)

        items = []
        for p in products:
            offers = await self._offers.get_by_product(p.id, sort_by="delivery_date")
            nearest = offers[0].delivery_date if offers else None
            avg_rating, review_count = ratings.get(p.id, (None, 0))
            thumbnail_url = (
                self._image_service.get_object_url(p.thumbnail_object_key)
                if self._image_service and p.thumbnail_object_key
                else None
            )
            items.append(
                ProductListItemDTO(
                    id=p.id,
                    name=p.name,
                    thumbnail_url=thumbnail_url,
                    price=MoneyDTO(amount=p.price_amount, currency=p.price_currency),
                    stock=p.stock,
                    nearest_delivery_date=nearest,
                    avg_rating=avg_rating,
                    review_count=review_count,
                )
            )

        return ProductListResponseDTO(
            items=items,
            next_cursor=str(next_cursor) if next_cursor else None,
        )


class GetPublicProductDetailsHandler:
    def __init__(
        self,
        product_repo: ProductRepository,
        attr_repo: ProductAttributeRepository,
        offer_repo: OfferRepository,
        seller_repo: SellerRepository,
        image_service: IImageService | None = None,
    ):
        self._products = product_repo
        self._attrs = attr_repo
        self._offers = offer_repo
        self._sellers = seller_repo
        self._image_service = image_service

    async def handle(self, query: GetPublicProductDetailsQuery) -> ProductDetailsDTO:
        product = await self._products.get_by_id(query.product_id)
        if not product:
            raise EntityNotFound("Product not found")

        attrs = await self._attrs.get_by_product(query.product_id)
        offers = await self._offers.get_by_product(query.product_id, sort_by=query.offers_sort)

        offer_dtos = []
        for o in offers:
            seller = await self._sellers.get_by_id(o.seller_id)
            offer_dtos.append(
                OfferDTO(
                    id=o.id,
                    seller=SellerDTO(id=seller.id, name=seller.name, rating=seller.rating),
                    price=MoneyDTO(amount=o.price_amount, currency=o.price_currency),
                    delivery_date=o.delivery_date,
                )
            )

        ratings = await self._products.get_ratings([product.id])
        avg_rating, review_count = ratings.get(product.id, (None, 0))

        category_name = None
        if product.category_id:
            category_name = await self._products.get_category_name(product.category_id)

        min_offer = min(offers, key=lambda o: o.price_amount) if offers else None

        image_url = (
            self._image_service.get_object_url(product.image_object_key)
            if self._image_service and product.image_object_key
            else None
        )

        return ProductDetailsDTO(
            id=product.id,
            name=product.name,
            description=product.description,
            image_url=image_url,
            attributes=[ProductAttributeDTO(key=a.key, value=a.value) for a in attrs],
            offers=offer_dtos,
            avg_rating=avg_rating,
            review_count=review_count,
            sku=product.sku,
            min_price=MoneyDTO(amount=min_offer.price_amount, currency=min_offer.price_currency)
            if min_offer
            else None,
            category_name=category_name,
        )


class AdminListProductsHandler:
    def __init__(
        self,
        product_repo: ProductRepository,
        attr_repo: ProductAttributeRepository,
        image_service: IImageService | None = None,
    ):
        self._products = product_repo
        self._attrs = attr_repo
        self._image_service = image_service

    async def handle(self, query: AdminListProductsQuery) -> dict:
        cursor_uuid = uuid.UUID(query.cursor) if query.cursor else None
        products, next_cursor = await self._products.get_list(
            query.limit,
            cursor_uuid,
            sort=query.sort,
            search=query.search,
            is_active=query.is_active,
            in_stock=query.in_stock,
            price_min=query.price_min,
            price_max=query.price_max,
        )
        items = []
        for p in products:
            attrs = await self._attrs.get_by_product(p.id)
            image_url = (
                self._image_service.get_object_url(p.image_object_key)
                if self._image_service and p.image_object_key
                else None
            )
            thumbnail_url = (
                self._image_service.get_object_url(p.thumbnail_object_key)
                if self._image_service and p.thumbnail_object_key
                else None
            )
            items.append(
                AdminProductResponseDTO(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    sku=p.sku,
                    category_id=p.category_id,
                    price=MoneyDTO(amount=p.price_amount, currency=p.price_currency),
                    stock=p.stock,
                    is_active=p.is_active,
                    image_url=image_url,
                    thumbnail_url=thumbnail_url,
                    attributes=[ProductAttributeDTO(key=a.key, value=a.value) for a in attrs],
                )
            )
        return {"items": items, "next_cursor": str(next_cursor) if next_cursor else None}


class AdminGetProductHandler:
    def __init__(
        self,
        product_repo: ProductRepository,
        attr_repo: ProductAttributeRepository,
        image_service: IImageService | None = None,
    ):
        self._products = product_repo
        self._attrs = attr_repo
        self._image_service = image_service

    async def handle(self, query: AdminGetProductQuery) -> AdminProductResponseDTO:
        product = await self._products.get_by_id(query.product_id)
        if not product:
            raise EntityNotFound("Product not found")
        attrs = await self._attrs.get_by_product(query.product_id)
        image_url = (
            self._image_service.get_object_url(product.image_object_key)
            if self._image_service and product.image_object_key
            else None
        )
        thumbnail_url = (
            self._image_service.get_object_url(product.thumbnail_object_key)
            if self._image_service and product.thumbnail_object_key
            else None
        )
        return AdminProductResponseDTO(
            id=product.id,
            name=product.name,
            description=product.description,
            sku=product.sku,
            category_id=product.category_id,
            price=MoneyDTO(amount=product.price_amount, currency=product.price_currency),
            stock=product.stock,
            is_active=product.is_active,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            attributes=[ProductAttributeDTO(key=a.key, value=a.value) for a in attrs],
        )
