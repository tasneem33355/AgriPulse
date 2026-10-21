import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.generator import rag_generator

app = FastAPI(
    title="AgriPulse - Maintenance RAG Assistant & Work Order Generator",
    description="FMEA-powered LLM/RAG Assistant generating actionable maintenance work orders for irrigation pumps.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DiagnosticInputPayload(BaseModel):
    pump_id: str = "PUMP_001"
    timestamp: Optional[str] = None
    status: str
    health_index_pct: float
    risk_score: float
    attributed_sensor: str
    primary_diagnosis: Optional[Dict[str, Any]] = None
    sensor_contributions_pct: Optional[Dict[str, float]] = None
    differential_diagnostics: Optional[list] = None
    recommended_spare_parts: Optional[list] = None
    required_inspection_tools: Optional[list] = None

@app.get("/health", tags=["Monitoring"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "agripulse-rag-service",
        "indexed_fmea_documents": len(rag_generator.fmea_cache)
    }

@app.post("/generate-work-order", tags=["RAG Assistant"])
def generate_work_order(payload: DiagnosticInputPayload):
    """
    Accepts diagnostic anomaly from inference-service and synthesizes
    an ISO/FMEA compliant maintenance work order for dashboard technicians.
    """
    try:
        data_dict = payload.model_dump()
        work_order = rag_generator.generate_work_order(data_dict)
        return work_order
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating work order: {str(e)}"
        )

@app.get("/knowledge-base/list", tags=["Knowledge Base"])
def list_knowledge_base():
    return {
        "fmea_documents": list(rag_generator.fmea_cache.keys()),
        "total_documents": len(rag_generator.fmea_cache)
    }
