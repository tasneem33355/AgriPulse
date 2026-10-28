from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime

class SensorReadingInput(BaseModel):
    pump_id: str = Field(default="PUMP_001", description="Unique pump telemetry identifier")
    timestamp: datetime = Field(description="ISO-8601 UTC timestamp of current reading")
    mode: Optional[str] = Field(default="industrial", description="'industrial' for two-stage asset, or 'prototype' for 12V DC test rig")
    sensor_00: float = Field(description="Motor Drive-End Bearing Radial Vibration")
    sensor_04: float = Field(description="Motor Shaft Rotational Speed")
    sensor_05: float = Field(description="Motor Current Phase A / DC Current")
    sensor_11: float = Field(description="Motor Current Phase B (or replicated single current for DC)")
    sensor_13: float = Field(description="Coupling Axial Vibration")
    sensor_28: float = Field(description="Stage 2 Impeller Speed (or scaled Flow for prototype)")
    sensor_40: float = Field(description="Thrust Bearing Temperature")
    sensor_48: Optional[float] = Field(default=None, description="Inlet / Suction Pressure")

class RankedAttributionItem(BaseModel):
    sensor_id: str
    sensor_name: str
    subsystem: str
    deviation_direction: str
    z_score: float
    contribution_pct: float
    fmea_reference: str

class DiagnosticSummary(BaseModel):
    attributed_sensor: str
    sensor_name: str
    subsystem: str
    direction: str
    deviation_z_score: float
    fault_category: str
    hypothesis_title: str
    engineering_rationale: str
    fmea_reference_file: str
    recommended_primary_action: str
    methodology_note: str
    urgency: str

class PredictionOutput(BaseModel):
    pump_id: str
    timestamp: datetime
    mode: str
    status: str  # INITIALIZING, NORMAL, WARNING, CRITICAL
    health_index_pct: float
    risk_score: float
    smooth_risk_score: float
    model_used: bool
    buffer_ready: bool
    buffer_fill_pct: float
    persistence_active_mins: int
    attributed_sensor: Optional[str] = None
    attribution_summary: Optional[DiagnosticSummary] = None
    sensor_contributions_pct: Optional[Dict[str, float]] = None
    ranked_anomalies: Optional[List[RankedAttributionItem]] = None
    stagnation_alerts: Optional[List[Dict[str, Any]]] = None
    current_readings: Optional[Dict[str, float]] = None

class AIChatRequest(BaseModel):
    user_query: str = Field(description="Technician question or troubleshooting query")
    pump_id: Optional[str] = Field(default="PUMP_001", description="Monitored pump asset identifier")
    sensor_diagnostics: Optional[Dict[str, Any]] = Field(default=None, description="Current telemetry and diagnostic payload from /predict")

class AIChatResponse(BaseModel):
    response: str
    timestamp: datetime
    model: str = "llama-3.3-70b-versatile"

class WorkOrderRequest(BaseModel):
    pump_id: Optional[str] = Field(default="PUMP_001", description="Monitored pump asset identifier")
    sensor_diagnostics: Dict[str, Any] = Field(description="Active diagnostic payload from /predict requiring work order")

class WorkOrderResponse(BaseModel):
    work_order_id: str
    pump_id: str
    generated_at: str
    urgency: str
    failure_diagnosis: str
    standards_reference: str
    immediate_mitigation: List[str]
    loto_safety_steps: List[str]
    inspection_checklist: List[str]
    required_parts_and_tools: List[str]
    estimated_downtime_hours: float
    llm_generated: bool
