import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base" / "fmea"

class WorkOrderRAGGenerator:
    """
    RAG-driven Work Order and Maintenance Recommendation Generator.
    Loads domain FMEA standards and generates production-ready maintenance orders.
    """

    def __init__(self, kb_path: Path = KNOWLEDGE_BASE_DIR):
        self.kb_path = kb_path
        self.fmea_cache: Dict[str, str] = {}
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        if not self.kb_path.exists():
            return
        for file in self.kb_path.glob("*.md"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    self.fmea_cache[file.name] = f.read()
                print(f"[RAG] Indexed FMEA document: {file.name}")
            except Exception as e:
                print(f"[RAG] Error loading {file.name}: {e}")

    def generate_work_order(self, diagnostic_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes model anomaly telemetry with FMEA domain knowledge
        to produce an actionable, standard-compliant work order.
        """
        pump_id = diagnostic_payload.get("pump_id", "PUMP_001")
        timestamp = diagnostic_payload.get("timestamp", datetime.utcnow().isoformat())
        status = diagnostic_payload.get("status", "WARNING")
        health_index = diagnostic_payload.get("health_index_pct", 50.0)
        risk_score = diagnostic_payload.get("risk_score", 0.3)
        attributed_sensor = diagnostic_payload.get("attributed_sensor", "sensor_13")

        primary_diag = diagnostic_payload.get("primary_diagnosis", {}) or {}
        fault_title = primary_diag.get("title", "Mechanical / Electrical Anomaly")
        subsystem = primary_diag.get("subsystem", "General Pump Train")
        iso_standard = primary_diag.get("iso_standard", "ISO 10816-3 Class II")
        fmea_file = primary_diag.get("fmea_document", "fmea_coupling_misalignment_and_wear.md")
        urgency = primary_diag.get("urgency", "HIGH")

        # Fetch relevant FMEA content
        fmea_content = self.fmea_cache.get(fmea_file, "")

        # Extract checklist steps from FMEA markdown
        checklist_steps = []
        if fmea_content:
            in_checklist = False
            for line in fmea_content.splitlines():
                if "4. Maintenance Checklist" in line:
                    in_checklist = True
                    continue
                elif line.startswith("## 5."):
                    in_checklist = False
                    break
                if in_checklist and (line.strip().startswith("1.") or line.strip().startswith("2.") or
                                     line.strip().startswith("3.") or line.strip().startswith("4.") or
                                     line.strip().startswith("5.") or line.strip().startswith("6.")):
                    checklist_steps.append(line.strip())

        if not checklist_steps:
            checklist_steps = [
                "1. Perform electrical Lockout/Tagout (LOTO) on pump feeder panel.",
                "2. Conduct physical inspection of attributed component.",
                "3. Verify vibration RMS velocity with handheld vibration pen.",
                "4. Check alignment tolerances and fastener torques.",
                "5. Rotate pump shaft manually to verify free rotation without binding."
            ]

        # Generate unique work order ID
        wo_id = f"WO-{pump_id}-{datetime.utcnow().strftime('%Y%m%d%H%M')}"

        work_order = {
            "work_order_id": wo_id,
            "pump_id": pump_id,
            "asset_name": "Grundfos NB / Kirloskar DB Centrifugal Irrigation Pump",
            "generated_at": timestamp,
            "alert_status": status,
            "health_index_pct": health_index,
            "risk_score": risk_score,
            "attributed_sensor": attributed_sensor,
            "subsystem": subsystem,
            "primary_diagnosis": fault_title,
            "governing_standard": iso_standard,
            "urgency": urgency,
            "estimated_lead_time_buffer": "30 to 60 minutes remaining before functional trip",
            "fmea_reference_source": fmea_file,
            "differential_possibilities": diagnostic_payload.get("differential_diagnostics", []),
            "sensor_contributions_breakdown": diagnostic_payload.get("sensor_contributions_pct", {}),
            "step_by_step_inspection_checklist": checklist_steps,
            "required_spare_parts": diagnostic_payload.get("recommended_spare_parts", [
                "Replacement seals / gaskets",
                "Alignment shims"
            ]),
            "required_tools_and_instruments": diagnostic_payload.get("required_inspection_tools", [
                "Dial indicator set",
                "True-RMS Multimeter",
                "Torque wrench"
            ]),
            "approval_status": "DRAFT_PENDING_ENGINEER_REVIEW"
        }

        return work_order

rag_generator = WorkOrderRAGGenerator()
