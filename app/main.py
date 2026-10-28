import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.schemas import (
    SensorReadingInput, PredictionOutput,
    AIChatRequest, AIChatResponse,
    WorkOrderRequest, WorkOrderResponse
)
from app.engine import engine_registry
from app.config import MODEL_CONFIG, WARNING_THRESHOLD, CRITICAL_THRESHOLD
from rag_engine import ask_ai_assistant, generate_work_order, get_groq_api_key

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

    rag_ready = bool(get_groq_api_key()) and os.path.exists("./chroma_db")

    return {
        "status": service_status,
        "service": "agripulse-integrated-service",
        "model_loaded": is_loaded,
        "rag_available": rag_ready,
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

@app.post("/ai/chat", response_model=AIChatResponse, tags=["AI Assistant"])
def chat_with_assistant(payload: AIChatRequest):
    """
    Interactive technical assistant for pump engineers and field technicians.
    Combines live telemetry diagnosis with retrieved ISO/ANSI/FMEA engineering standards.
    """
    try:
        response_text = ask_ai_assistant(
            user_query=payload.user_query,
            sensor_diagnostics=payload.sensor_diagnostics
        )
        return {
            "response": response_text,
            "timestamp": datetime.utcnow(),
            "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Assistant query error: {str(e)}"
        )

@app.post("/ai/work-order", response_model=WorkOrderResponse, tags=["Work Orders"])
def create_work_order(payload: WorkOrderRequest):
    """
    Generates a formal, production-ready Maintenance Work Order JSON payload.
    Uses RAG context (FMEA, LOTO safety checklist, spare parts, torque specs)
    with guaranteed deterministic fallback if LLM is offline.
    """
    try:
        wo = generate_work_order(payload.sensor_diagnostics)
        return wo
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Work Order generation error: {str(e)}"
        )

@app.get("/config", tags=["Configuration"])
def get_service_config():
    """Returns active model metadata, sensor list, and validation metrics."""
    return MODEL_CONFIG
