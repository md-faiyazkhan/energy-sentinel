from fastapi import APIRouter
from src.services.analytics_service import AnalyticsService
from src.schemas.analytics import HourlyPattern, WeekdayWeekendPattern, PeakHour, DailyActivityRate

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/hourly-pattern/{appliance}", response_model=list[HourlyPattern])
def get_hourly_pattern(appliance: str):
    """
    Returns average power consumption per hour of day for an appliance.
    """
    service = AnalyticsService()
    return service.get_hourly_pattern(appliance)


@router.get("/weekday-vs-weekend/{appliance}", response_model=WeekdayWeekendPattern)
def get_weekday_vs_weekend(appliance: str):
    """
    Returns weekday vs weekend hourly power consumption for an appliance.
    """
    service = AnalyticsService()
    return service.get_weekday_vs_weekend(appliance)


@router.get("/peak-hour/{appliance}", response_model=PeakHour)
def get_peak_hour(appliance: str):
    """
    Returns peak usage hour for an appliance.
    """
    service = AnalyticsService()
    return service.get_peak_hour(appliance)


@router.get("/daily-activity/{appliance}", response_model=list[DailyActivityRate])
def get_daily_activity(appliance: str):
    """
    Returns daily activity rate for an appliance.
    """
    service = AnalyticsService()
    return service.get_daily_activity_rate(appliance)