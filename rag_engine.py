"""
AgriPulse RAG & AI Maintenance Assistant Engine.
Provides:
1. Interactive technical maintenance chat with RAG context (ask_ai_assistant).
2. Autonomous formal engineering Work Order generation (generate_work_order).
Powered by LangChain, ChromaDB vector store, and Groq LLM (llama-3.3-70b-versatile).
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger("agripulse.rag")

# Lazy-loaded globals
_embeddings = None
_vector_store = None
_retriever = None
_llm = None

DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def get_groq_api_key() -> Optional[str]:
    return os.getenv("GROQ_API_KEY")

def get_retriever():
    """Lazy initialize vector database and embeddings on first query."""
    global _embeddings, _vector_store, _retriever
    if _retriever is not None:
        return _retriever

    if not os.path.exists(DB_DIR):
        logger.warning(f"ChromaDB directory '{DB_DIR}' not found. Retrieval will be empty.")
        return None

    try:
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings

        if _embeddings is None:
            _embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )

        _vector_store = Chroma(
            persist_directory=DB_DIR,
            embedding_function=_embeddings
        )
        _retriever = _vector_store.as_retriever(search_kwargs={"k": 4})
        return _retriever
    except Exception as e:
        logger.error(f"Failed to load ChromaDB retriever: {e}")
        return None

def get_llm():
    """Lazy initialize Groq LLM."""
    global _llm
    if _llm is not None:
        return _llm

    api_key = get_groq_api_key()
    if not api_key:
        logger.warning("GROQ_API_KEY is not set. LLM generation disabled.")
        return None

    try:
        from langchain_groq import ChatGroq
        _llm = ChatGroq(
            model=GROQ_MODEL,
            api_key=api_key,
            temperature=0.15,
            max_retries=2,
            timeout=45
        )
        return _llm
    except Exception as e:
        logger.error(f"Failed to initialize ChatGroq: {e}")
        return None


SYSTEM_PROMPT = """You are AgriPulse, an expert Reliability & Predictive Maintenance Engineer for industrial two-stage centrifugal irrigation pumping systems.

You receive:
1. Operational telemetry, health index, and real-time diagnostic hypotheses.
2. Retrieved technical documentation (ISO 10816-3, ANSI/HI 9.6, FMEA manuals).
3. The maintenance technician's query or work order request.

GUIDELINES:
- Prioritize confirmed multi-sensor diagnostic evidence (e.g. coupling vibration vs. motor DE vibration).
- Provide precise, actionable engineering recommendations with safety first (LOTO protocols).
- Distinguish confirmed symptoms from unverified hypotheses.
- Never invent fictitious numbers or claims. If evidence is missing, state clearly what needs inspection.
- Ground advice in pump engineering standards (ISO 10816-3 Class II).
"""

def _build_search_query(user_query: str, diagnostics: Optional[Dict[str, Any]]) -> str:
    parts = [user_query]
    if diagnostics:
        summary = diagnostics.get("attribution_summary")
        if isinstance(summary, dict):
            parts.append(summary.get("hypothesis_title", ""))
            parts.append(summary.get("fault_category", ""))
            parts.append(summary.get("fmea_reference_file", ""))
        elif summary:
            parts.append(str(summary))

        if diagnostics.get("attributed_sensor"):
            parts.append(f"sensor: {diagnostics['attributed_sensor']}")
        if diagnostics.get("status"):
            parts.append(f"status: {diagnostics['status']}")
    return " ".join([p for p in parts if p]).strip()


def ask_ai_assistant(
    user_query: str,
    sensor_diagnostics: Optional[Dict[str, Any]] = None
) -> str:
    """Conversational technical Q&A assistant for pump maintenance technicians."""
    llm = get_llm()
    retriever = get_retriever()

    if not llm:
        return (
            "AgriPulse AI Assistant is in offline mode (GROQ_API_KEY not configured). "
            "Please configure your GROQ_API_KEY in the environment."
        )

    # 1. Retrieve knowledge chunks
    context_chunks = []
    if retriever:
        try:
            search_text = _build_search_query(user_query, sensor_diagnostics)
            docs = retriever.invoke(search_text)
            for idx, doc in enumerate(docs, 1):
                src = doc.metadata.get("source", "Technical Manual")
                context_chunks.append(f"[Source {idx}: {os.path.basename(src)}]\n{doc.page_content}")
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")

    context_str = "\n\n".join(context_chunks) if context_chunks else "No specific document retrieved."
    diag_str = json.dumps(sensor_diagnostics or {}, ensure_ascii=False, indent=2, default=str)

    # 2. Invoke LLM
    try:
        from langchain_core.prompts import ChatPromptTemplate
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT + "\n\n[RETRIEVED KNOWLEDGE]\n{context}\n\n[LIVE TELEMETRY & DIAGNOSTICS]\n{diagnostics}"),
            ("human", "{query}")
        ])

        chain = prompt | llm
        resp = chain.invoke({
            "context": context_str,
            "diagnostics": diag_str,
            "query": user_query
        })
        return resp.content if hasattr(resp, "content") else str(resp)
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        return f"Could not generate AI response: {str(e)}"


def generate_work_order(sensor_diagnostics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a structured, production-ready Maintenance Work Order JSON payload.
    Falls back gracefully to deterministic rule-based work orders if LLM is offline.
    """
    pump_id = sensor_diagnostics.get("pump_id", "PUMP_001")
    status = sensor_diagnostics.get("status", "WARNING")
    health_idx = sensor_diagnostics.get("health_index_pct", 65.0)
    attributed_sensor = sensor_diagnostics.get("attributed_sensor", "sensor_13")
    summary = sensor_diagnostics.get("attribution_summary") or {}

    fault_cat = summary.get("fault_category", "Mechanical Anomaly")
    hypo_title = summary.get("hypothesis_title", "Operational Deviation Detected")
    action = summary.get("recommended_primary_action", "Inspect physical pump components.")

    work_order_id = f"WO-{pump_id}-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    urgency = "CRITICAL — Immediate Inspection within 30m" if status == "CRITICAL" else "WARNING — Action within 2 hours"

    # Try LLM-powered structured generation
    llm = get_llm()
    retriever = get_retriever()

    if llm and retriever:
        try:
            query = f"Generate work order for {fault_cat}: {hypo_title} on {pump_id}"
            docs = retriever.invoke(f"{fault_cat} {hypo_title} maintenance checklist")
            context_str = "\n\n".join([d.page_content for d in docs[:3]])

            prompt_text = f"""Based on the pump failure diagnosis and standards below, generate a STRICT JSON object for an industrial work order.
Do not output markdown code blocks or explanations, ONLY pure JSON.

Asset: Two-Stage Centrifugal Irrigation Pump ({pump_id})
Status: {status} (Health Index: {health_idx}%)
Diagnosed Issue: {fault_cat} - {hypo_title}
Primary Sensor: {attributed_sensor}
Context: {context_str}

Required JSON keys:
{{
  "work_order_id": "{work_order_id}",
  "pump_id": "{pump_id}",
  "urgency": "{urgency}",
  "failure_diagnosis": "<specific diagnosis>",
  "standards_reference": "<e.g. ISO 10816-3 / ANSI HI 9.6>",
  "immediate_mitigation": ["<step 1>", "<step 2>"],
  "loto_safety_steps": ["<step 1>", "<step 2>"],
  "inspection_checklist": ["<check 1>", "<check 2>", "<check 3>"],
  "required_parts_and_tools": ["<part 1>", "<tool 1>"],
  "estimated_downtime_hours": <number>
}}
"""
            resp = llm.invoke(prompt_text)
            raw = resp.content if hasattr(resp, "content") else str(resp)
            clean_json = raw.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.startswith("```"):
                clean_json = clean_json[3:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            clean_json = clean_json.strip()

            parsed = json.loads(clean_json)
            parsed["work_order_id"] = work_order_id
            parsed["generated_at"] = datetime.utcnow().isoformat()
            parsed["llm_generated"] = True
            return parsed
        except Exception as e:
            logger.warning(f"LLM Work order generation fallback triggered: {e}")

    # Deterministic Rule-Based Fallback (guaranteed 100% uptime)
    return {
        "work_order_id": work_order_id,
        "pump_id": pump_id,
        "generated_at": datetime.utcnow().isoformat(),
        "urgency": urgency,
        "failure_diagnosis": f"{fault_cat}: {hypo_title}",
        "standards_reference": "ISO 10816-3 Class II / ANSI-HI 9.6 Centrifugal Standards",
        "immediate_mitigation": [
            f"Reduce operational load on {pump_id} if vibration continues to climb.",
            action
        ],
        "loto_safety_steps": [
            "1. De-energize and lock out motor feeder circuit breaker (LOTO protocol).",
            "2. Verify zero-voltage across stator leads using calibrated multimeter.",
            "3. Close and lock suction and discharge isolation valves."
        ],
        "inspection_checklist": [
            f"1. Visually and acoustically inspect {attributed_sensor} mounting point.",
            "2. Rotate pump shaft 360 degrees by hand to check for binding or friction.",
            "3. Verify hold-down bolt torques and elastomeric coupling insert condition.",
            "4. Measure bearing surface temperature with infrared pyrometer."
        ],
        "required_parts_and_tools": [
            "Reverse dial indicator set / Laser alignment tool",
            "Calibrated torque wrench (M12 grade 8.8)",
            "Replacement elastomeric spider insert / SKF EP2 grease"
        ],
        "estimated_downtime_hours": 1.5,
        "llm_generated": False
    }
