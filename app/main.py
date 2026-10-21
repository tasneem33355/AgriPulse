import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.schemas import SensorReadingInput, PredictionOutput
from app.engine import engine_registry
from app.config import MODEL_CONFIG, WARNING_THRESHOLD, CRITICAL_THRESHOLD

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=== AgriPulse Predictive Maintenance Service Starting ===")
    print(f"Operational Warning Threshold: {WARNING_THRESHOLD} | Critical Threshold: {CRITICAL_THRESHOLD}")
    yield
    print("=== AgriPulse Predictive Maintenance Service Shutting Down ===")

app = FastAPI(
    title="AgriPulse - Centrifugal Pump Predictive Maintenance Service",
    description="Causal Time-Series Anomaly Detection & Statistical Attribution for Industrial Irrigation Pumping Systems.",
    version="2.1.0",
    lifespan=lifespan
)

# CORS: Configurable from environment, defaults to open for dashboard integration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Monitoring"])
def health_check():
    """Returns dynamic service health, model load state, and active thresholds."""
    is_loaded = engine_registry.loaded_model is not None
    service_status = "HEALTHY" if is_loaded else "DEGRADED"

    return {
        "status": service_status,
        "service": "agripulse-inference-service",
        "model_loaded": is_loaded,
        "active_pumps_tracked": len(engine_registry.engines),
        "calibrated_thresholds": {
            "warning": WARNING_THRESHOLD,
            "critical": CRITICAL_THRESHOLD
        }
    }

@app.post("/predict", response_model=PredictionOutput, tags=["Inference"])
def predict_pump_health(payload: SensorReadingInput):
    """
    Ingests 1-minute telemetry packet, maintains 65-min causal rolling memory,
    and returns real-time risk score, health index, and statistical anomaly attribution.
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
    """Returns active model metadata, sensor list, and validation metrics."""
    return MODEL_CONFIG
