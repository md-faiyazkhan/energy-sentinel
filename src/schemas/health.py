from pydantic import BaseModel


class RecentAnomaly(BaseModel):
    timestamp: str
    power_watts: float
    anomaly_score: float
    risk_level: str


class ApplianceHealth(BaseModel):
    appliance: str
    total_records: int
    anomaly_count: int
    anomaly_pct: float
    risk_distribution: dict
    recent_anomalies: list


class ApplianceHealthSummary(BaseModel):
    appliance: str
    anomaly_count: int
    high_risk_count: int
    overall_status: str