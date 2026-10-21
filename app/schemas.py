from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime

class SensorReadingInput(BaseModel):
    pump_id: str = Field(default="PUMP_001", description="Identifier of monitored pump asset")
    timestamp: datetime = Field(description="ISO-8601 UTC timestamp of telemetry sample")
    sensor_00: float = Field(description="Motor DE Bearing Radial Vibration (ADXL345 RMS)")
    sensor_04: float = Field(default=2940.0, description="Motor Shaft Rotational Speed (RPM)")
    sensor_05: float = Field(description="Motor Stator Phase A Current Draw (Amperes RMS)")
    sensor_11: float = Field(description="Motor Stator Phase B Current Draw (Amperes RMS)")
    sensor_13: float = Field(description="Coupling Axial Vibration (ADXL345 RMS)")
    sensor_28: float = Field(default=180.0, description="Discharge Hydraulic Flow Rate (L/min)")
    sensor_40: float = Field(description="Bearing Housing Surface Temperature (Celsius)")
    sensor_48: Optional[float] = Field(default=None, description="Optional Discharge Pressure (bar)")

class DifferentialFaultItem(BaseModel):
    fault_code: str
    fault_title: str
    confidence_pct: float
    fmea_reference: str

class PrimaryDiagnosis(BaseModel):
    fault_code: str
    title: str
    subsystem: str
    confidence_pct: float
    iso_standard: str
    fmea_document: str
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
    primary_diagnosis: Optional[PrimaryDiagnosis] = None
    sensor_contributions_pct: Optional[Dict[str, float]] = None
    differential_diagnostics: Optional[List[DifferentialFaultItem]] = None
    recommended_spare_parts: Optional[List[str]] = None
    required_inspection_tools: Optional[List[str]] = None
    current_readings: Optional[Dict[str, float]] = None
