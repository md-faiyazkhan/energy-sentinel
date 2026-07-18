from fastapi import APIRouter
from src.services.monitoring_service import MonitoringService
from src.schemas.monitoring import MonitoringSummary, MonthlyTrend, ApplianceEnergy

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/summary", response_model=MonitoringSummary)
def get_summary():
    """
    Returns high-level energy consumption summary.
    """
    service = MonitoringService()
    return service.get_summary()


@router.get("/monthly-trend", response_model=list[MonthlyTrend])
def get_monthly_trend():
    """
    Returns monthly average power consumption trend.
    """
    service = MonitoringService()
    return service.get_monthly_trend()


@router.get("/appliance-breakdown", response_model=list[ApplianceEnergy])
def get_appliance_breakdown():
    """
    Returns total energy consumed per appliance in kWh.
    """
    service = MonitoringService()
    return service.get_appliance_energy_breakdown()