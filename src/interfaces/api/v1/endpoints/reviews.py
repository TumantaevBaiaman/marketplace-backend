import uuid

from fastapi import APIRouter, Depends

from src.application.commands.review_commands import CreateReviewCommand
from src.application.dto.review_dto import ReviewCreateDTO, ReviewListDTO, ReviewResponseDTO
from src.application.queries.review_queries import GetMyReviewQuery, ListReviewsQuery
from src.application.services.review_service import ReviewService
from src.interfaces.api.v1.dependencies import get_current_user, get_review_service

router = APIRouter(prefix="/public/products/{product_id}/reviews", tags=["Reviews"])


@router.get("/", response_model=ReviewListDTO)
async def list_reviews(
    product_id: uuid.UUID,
    service: ReviewService = Depends(get_review_service),
) -> ReviewListDTO:
    return await service.list_reviews(ListReviewsQuery(product_id=product_id))


@router.get("/my", response_model=ReviewResponseDTO | None)
async def get_my_review(
    product_id: uuid.UUID,
    service: ReviewService = Depends(get_review_service),
    current_user: dict = Depends(get_current_user),
) -> ReviewResponseDTO | None:
    user_id = uuid.UUID(current_user["sub"])
    return await service.get_my_review(GetMyReviewQuery(product_id=product_id, user_id=user_id))


@router.post("/", response_model=ReviewResponseDTO, status_code=201)
async def create_review(
    product_id: uuid.UUID,
    dto: ReviewCreateDTO,
    service: ReviewService = Depends(get_review_service),
    current_user: dict = Depends(get_current_user),
) -> ReviewResponseDTO:
    user_id = uuid.UUID(current_user["sub"])
    return await service.create(
        CreateReviewCommand(
            product_id=product_id,
            user_id=user_id,
            author=dto.author,
            rating=dto.rating,
            text=dto.text,
        )
    )
