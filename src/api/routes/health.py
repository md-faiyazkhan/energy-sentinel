from fastapi import APIRouter
from src.services.health_service import HealthService
from src.schemas.health import ApplianceHealth, ApplianceHealthSummary

router = APIRouter(prefix="/health", tags=["Appliance Health"])


@router.get("/summary", response_model=list[ApplianceHealthSummary])
def get_all_health_summary():
    """
    Returns health status summary for all appliances.
    """
    service = HealthService()
    return service.get_all_health_summary()


@router.get("/{appliance}", response_model=ApplianceHealth)
def get_appliance_health(appliance: str):
    """
    Returns detailed anomaly detection results for a single appliance.
    """
    service = HealthService()
    return service.get_appliance_health(appliance)