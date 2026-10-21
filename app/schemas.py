from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime

class SensorReadingInput(BaseModel):
    pump_id: str = Field(default="PUMP_001", description="Unique pump telemetry identifier")
    timestamp: datetime = Field(description="ISO-8601 UTC timestamp of current reading")
    sensor_00: float = Field(description="Motor Drive-End Bearing Radial Vibration telemetry")
    sensor_04: float = Field(description="Motor Shaft Rotational Speed telemetry")
    sensor_05: float = Field(description="Motor Current Phase A telemetry")
    sensor_11: float = Field(description="Motor Current Phase B telemetry")
    sensor_13: float = Field(description="Coupling Axial Vibration telemetry")
    sensor_28: float = Field(description="Stage 2 Impeller Rotational Speed telemetry (historical values ~1050)")
    sensor_40: float = Field(description="Thrust Bearing Temperature telemetry")
    sensor_48: Optional[float] = Field(default=None, description="Inlet / Suction Line Pressure telemetry")

class RankedAttributionItem(BaseModel):
    sensor_id: str
    sensor_name: str
    subsystem: str
    deviation_direction: str  # ELEVATED or DEPRESSED
    z_score: float
    contribution_pct: float
    possible_fault_mode: str
    fmea_reference: str

class DiagnosticSummary(BaseModel):
    attributed_sensor: str
    sensor_name: str
    subsystem: str
    direction: str
    deviation_z_score: float
    attributed_failure_hypothesis: str
    methodology_note: str
    urgency: str

class PredictionOutput(BaseModel):
    pump_id: str
    timestamp: datetime
    status: str  # INITIALIZING, NORMAL, WARNING, CRITICAL
    health_index_pct: float
    risk_score: float
    smooth_risk_score: float
    buffer_ready: bool
    buffer_fill_pct: float
    attributed_sensor: Optional[str] = None
    attribution_summary: Optional[DiagnosticSummary] = None
    sensor_contributions_pct: Optional[Dict[str, float]] = None
    ranked_anomalies: Optional[List[RankedAttributionItem]] = None
    current_readings: Optional[Dict[str, float]] = None
