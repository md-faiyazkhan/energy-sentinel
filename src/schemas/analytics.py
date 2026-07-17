from pydantic import BaseModel


class HourlyPattern(BaseModel):
    hour: int
    avg_power_watts: float


class WeekdayWeekendPattern(BaseModel):
    weekday: list[HourlyPattern]
    weekend: list[HourlyPattern]


class PeakHour(BaseModel):
    appliance: str
    peak_hour: int
    peak_avg_power_watts: float


class DailyActivityRate(BaseModel):
    date: str
    activity_rate_pct: float