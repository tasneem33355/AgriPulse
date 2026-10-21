import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.schemas import SensorReadingInput, PredictionOutput
from app.engine import engine_registry
from app.config import MODEL_CONFIG, WARNING_THRESHOLD, CRITICAL_THRESHOLD

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=== AgriPulse AI Inference Service Starting ===")
    print(f"Warning Threshold: {WARNING_THRESHOLD} | Critical Threshold: {CRITICAL_THRESHOLD}")
    yield
    print("=== AgriPulse AI Inference Service Shutting Down ===")

app = FastAPI(
    title="AgriPulse - Centrifugal Pump AI Inference Service",
    description="Production Causal Anomaly Detection & Physics-Informed Diagnostics for Agricultural Irrigation Pumps.",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Monitoring"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "agripulse-inference-service",
        "active_pumps_tracked": len(engine_registry.engines),
        "model_loaded": engine_registry.loaded_model is not None,
        "calibrated_thresholds": {
            "warning": WARNING_THRESHOLD,
            "critical": CRITICAL_THRESHOLD
        }
    }

@app.post("/predict", response_model=PredictionOutput, tags=["Inference"])
def predict_pump_health(payload: SensorReadingInput):
    """
    Ingests 1-minute telemetry packet, updates rolling state, computes 28 causal features,
    and returns real-time risk score, health index, and physics-informed diagnosis.
    """
    try:
        engine = engine_registry.get_or_create(payload.pump_id)
        reading_dict = payload.model_dump()
        result = engine.process_reading(reading_dict)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error processing telemetry: {str(e)}"
        )

@app.get("/config", tags=["Configuration"])
def get_service_config():
    return MODEL_CONFIG
