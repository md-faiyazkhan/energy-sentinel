from fastapi import APIRouter
from src.services.recommendation_service import RecommendationService
from src.schemas.recommendations import Recommendation

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/", response_model=list[Recommendation])
def get_recommendations():
    """
    Returns rule-based recommendations for all appliances
    based on anomaly detection results.
    """
    service = RecommendationService()
    return service.get_recommendations()