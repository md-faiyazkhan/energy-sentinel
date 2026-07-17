from pydantic import BaseModel


class Recommendation(BaseModel):
    appliance: str
    anomaly_pct: float
    high_risk_count: int
    recommendation: str