from pydantic import BaseModel


class MonthlyTrend(BaseModel):
    month: str
    avg_power_watts: float


class ApplianceEnergy(BaseModel):
    appliance: str
    total_energy_kwh: float


class MonitoringSummary(BaseModel):
    total_energy_kwh: float
    avg_daily_kwh: float
    peak_power_watts: float
    avg_power_watts: float
    num_appliances: int
    date_range: dict