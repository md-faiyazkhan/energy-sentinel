from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from src.db.session import Base


class AnomalyLog(Base):
    """
    Stores anomaly detection results for each appliance.
    """
    __tablename__ = "anomaly_logs"

    id = Column(Integer, primary_key=True, index=True)
    appliance = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    power_watts = Column(Float, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    is_anomaly = Column(Boolean, nullable=False)
    risk_level = Column(String, nullable=False)  # Low, Medium, High
    created_at = Column(DateTime, default=datetime.utcnow)


class ApplianceMetadata(Base):
    """
    Stores static metadata for each appliance.
    """
    __tablename__ = "appliance_metadata"

    id = Column(Integer, primary_key=True, index=True)
    appliance = Column(String, unique=True, nullable=False, index=True)
    channel_id = Column(Integer, nullable=False)
    is_continuous = Column(Boolean, nullable=False)
    on_threshold_watts = Column(Float, nullable=False, default=5.0)
    created_at = Column(DateTime, default=datetime.utcnow)