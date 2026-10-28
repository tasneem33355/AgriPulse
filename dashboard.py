"""
AgriPulse — Real-Time Predictive Maintenance & Diagnostic Dashboard.
Interactive Streamlit application for end-to-end telemetry testing,
fault injection, ISA-18.2 debounce verification, and RAG work order generation.
"""

import os
import sys
import time
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import streamlit as st

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Page Configuration
st.set_page_config(
    page_title="AgriPulse — Smart Pump Predictive Maintenance",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .status-normal { color: #16a34a; font-weight: bold; }
    .status-warning { color: #d97706; font-weight: bold; }
    .status-critical { color: #dc2626; font-weight: bold; }
    .status-init { color: #64748b; font-weight: bold; }
    .badge-critical {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .badge-warning {
        background-color: #fef3c7;
        color: #92400e;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .badge-normal {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")

def check_backend_health():
    """Checks if FastAPI backend is live; returns details or offline fallback."""
    try:
        resp = requests.get(f"{API_BASE_URL}/health", timeout=1.5)
        if resp.status_code == 200:
            return True, resp.json()
    except Exception:
        pass
    return False, None

def call_predict_api(payload):
    """Sends telemetry packet via HTTP API or in-process engine fallback."""
    start_t = time.perf_counter()
    is_live, _ = check_backend_health()

    if is_live:
        try:
            resp = requests.post(f"{API_BASE_URL}/predict", json=payload, timeout=3.0)
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            if resp.status_code == 200:
                data = resp.json()
                data["_latency_ms"] = round(elapsed_ms, 2)
                data["_mode_used"] = "HTTP REST API (/predict)"
                return data
        except Exception as e:
            st.error(f"HTTP call failed: {e}")

    # In-Process Fallback
    from app.engine import engine_registry
    engine = engine_registry.get_or_create(payload.get("pump_id", "PUMP_001"))
    result = engine.process_reading(payload)
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0
    result["_latency_ms"] = round(elapsed_ms, 2)
    result["_mode_used"] = "In-Process Engine (Local Fallback)"
    return result

def call_work_order_api(diagnostics):
    """Generates work order via HTTP API or direct RAG engine."""
    is_live, _ = check_backend_health()
    if is_live:
        try:
            resp = requests.post(
                f"{API_BASE_URL}/ai/work-order",
                json={"pump_id": diagnostics.get("pump_id", "PUMP_001"), "sensor_diagnostics": diagnostics},
                timeout=20.0
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

    from rag_engine import generate_work_order
    return generate_work_order(diagnostics)

def call_ai_chat_api(query, diagnostics):
    """Sends chat query via HTTP API or direct RAG engine."""
    is_live, _ = check_backend_health()
    if is_live:
        try:
            resp = requests.post(
                f"{API_BASE_URL}/ai/chat",
                json={"user_query": query, "pump_id": diagnostics.get("pump_id", "PUMP_001"), "sensor_diagnostics": diagnostics},
                timeout=30.0
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception:
            pass

    from rag_engine import ask_ai_assistant
    return ask_ai_assistant(query, diagnostics)


# Session State Management
if "history" not in st.session_state:
    st.session_state.history = []
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None
if "current_minute" not in st.session_state:
    st.session_state.current_minute = 0
if "active_work_order" not in st.session_state:
    st.session_state.active_work_order = None


# --- SIDEBAR: Telemetry & Fault Injection Controller ---
st.sidebar.title("🎛️ Telemetry Controller")

backend_live, health_info = check_backend_health()
if backend_live:
    st.sidebar.success(f"🟢 API Connected: {API_BASE_URL}")
else:
    st.sidebar.info("🟡 In-Process Engine Mode (FastAPI offline)")

operating_mode = st.sidebar.selectbox(
    "Asset Operating Mode",
    ["industrial", "prototype"],
    help="'industrial' evaluates Two-Stage Municipal pump; 'prototype' uses adaptive relative Z-scaling for 12V DC rig."
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Fault Injection Presets")

preset = st.sidebar.selectbox(
    "Select Failure Scenario",
    [
        "🟢 Normal Baseline Operations",
        "🔴 Coupling Misalignment (Event 6)",
        "🟠 Impeller Mechanical Binding / Clogging",
        "🟡 Hydraulic Cavitation & Suction Loss",
        "🔵 Dry Running / Loss of Prime",
        "🟣 Sensor Flatline / Decoupling (Event 5)",
        "⚙️ Custom Manual Sliders"
    ]
)

# Preset Value Mapping
if operating_mode == "industrial":
    if "Normal" in preset:
        vals = {"s00": 1.50, "s04": 634.0, "s05": 76.0, "s11": 48.0, "s13": 2.00, "s28": 1055.0, "s40": 55.0}
    elif "Coupling" in preset:
        vals = {"s00": 2.80, "s04": 628.0, "s05": 78.5, "s11": 49.0, "s13": 8.50, "s28": 1045.0, "s40": 62.0}
    elif "Binding" in preset:
        vals = {"s00": 1.80, "s04": 590.0, "s05": 92.0, "s11": 55.0, "s13": 2.20, "s28": 720.0, "s40": 68.0}
    elif "Cavitation" in preset:
        vals = {"s00": 3.20, "s04": 632.0, "s05": 74.0, "s11": 47.0, "s13": 2.10, "s28": 680.0, "s40": 56.0}
    elif "Dry Running" in preset:
        vals = {"s00": 1.30, "s04": 642.0, "s05": 32.0, "s11": 25.0, "s13": 1.80, "s28": 1060.0, "s40": 76.0}
    elif "Flatline" in preset:
        vals = {"s00": 0.38, "s04": 202.0, "s05": 0.00, "s11": 48.0, "s13": 0.00, "s28": 233.0, "s40": 35.0}
    else:
        vals = {"s00": 1.50, "s04": 634.0, "s05": 76.0, "s11": 48.0, "s13": 2.00, "s28": 1055.0, "s40": 55.0}
else:
    # Prototype 12V DC test rig scale
    if "Normal" in preset:
        vals = {"s00": 0.25, "s04": 2500.0, "s05": 2.20, "s11": 2.20, "s13": 0.15, "s28": 5.0, "s40": 32.0}
    elif "Binding" in preset or "Coupling" in preset:
        vals = {"s00": 0.85, "s04": 2250.0, "s05": 3.80, "s11": 3.80, "s13": 0.80, "s28": 1.8, "s40": 42.0}
    else:
        vals = {"s00": 0.25, "s04": 2500.0, "s05": 2.20, "s11": 2.20, "s13": 0.15, "s28": 5.0, "s40": 32.0}

st.sidebar.markdown("#### Live Telemetry Inputs")
s00 = st.sidebar.number_input("sensor_00 (Motor Radial Vib)", value=float(vals["s00"]), step=0.1)
s04 = st.sidebar.number_input("sensor_04 (Motor Speed RPM)", value=float(vals["s04"]), step=5.0)
s05 = st.sidebar.number_input("sensor_05 (Motor Phase A / DC Current)", value=float(vals["s05"]), step=0.5)
s11 = st.sidebar.number_input("sensor_11 (Motor Phase B / Tap Current)", value=float(vals["s11"]), step=0.5)
s13 = st.sidebar.number_input("sensor_13 (Coupling Axial Vib)", value=float(vals["s13"]), step=0.2)
s28 = st.sidebar.number_input("sensor_28 (Stage-2 Impeller Speed / Flow)", value=float(vals["s28"]), step=10.0)
s40 = st.sidebar.number_input("sensor_40 (Thrust Bearing Temp °C)", value=float(vals["s40"]), step=1.0)

col_b1, col_b2 = st.sidebar.columns(2)

def send_current_telemetry():
    st.session_state.current_minute += 1
    t_stamp = datetime.utcnow() + timedelta(minutes=st.session_state.current_minute)
    payload = {
        "pump_id": "PUMP_DEMO_01",
        "timestamp": t_stamp.isoformat(),
        "mode": operating_mode,
        "sensor_00": float(s00),
        "sensor_04": float(s04),
        "sensor_05": float(s05),
        "sensor_11": float(s11),
        "sensor_13": float(s13),
        "sensor_28": float(s28),
        "sensor_40": float(s40)
    }
    res = call_predict_api(payload)
    st.session_state.last_prediction = res
    st.session_state.history.append({
        "minute": st.session_state.current_minute,
        "status": res["status"],
        "health_index": res["health_index_pct"],
        "risk_score": res["smooth_risk_score"],
        "latency_ms": res.get("_latency_ms", 0)
    })

if col_b1.button("▶️ Ingest 1-Min", use_container_width=True):
    send_current_telemetry()

if col_b2.button("⏩ Fast 61m Warmup", use_container_width=True):
    with st.spinner("Populating 61-minute causal warm-up buffer..."):
        from app.engine import engine_registry
        eng = engine_registry.get_or_create("PUMP_DEMO_01")
        base = datetime.utcnow()
        for i in range(61):
            st.session_state.current_minute += 1
            eng.process_reading({
                "pump_id": "PUMP_DEMO_01",
                "timestamp": (base + timedelta(minutes=st.session_state.current_minute)).isoformat(),
                "mode": operating_mode,
                "sensor_00": 1.50, "sensor_04": 634.0, "sensor_05": 76.0,
                "sensor_11": 48.0, "sensor_13": 2.00, "sensor_28": 1055.0, "sensor_40": 55.0
            })
        send_current_telemetry()
        st.success("Warm-up complete! Buffer is 100% full.")

if st.sidebar.button("🔄 Reset Telemetry Session", use_container_width=True):
    st.session_state.history = []
    st.session_state.last_prediction = None
    st.session_state.current_minute = 0
    st.session_state.active_work_order = None
    from app.engine import engine_registry
    engine_registry.engines.pop("PUMP_DEMO_01", None)
    st.rerun()


# --- MAIN INTERFACE ---
st.title("⚙️ AgriPulse: Industrial Condition Monitoring & RAG Copilot")
st.caption("Two-Stage Centrifugal Irrigation Pump Telemetry • ANSI/ISA-18.2 Alarm Persistence • Automated FMEA Work Orders")

pred = st.session_state.last_prediction

if not pred:
    st.info("👈 Use the Telemetry Controller in the sidebar to ingest real-time readings or click **'Fast 61m Warmup'** to start monitoring.")
else:
    # 1. Top Operational KPIs
    status = pred["status"]
    health = pred["health_index_pct"]
    risk = pred["smooth_risk_score"]
    pers = pred["persistence_active_mins"]
    lat = pred.get("_latency_ms", 0)
    mode_str = pred.get("_mode_used", "API")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    status_color = {
        "NORMAL": "badge-normal",
        "WARNING": "badge-warning",
        "CRITICAL": "badge-critical",
        "INITIALIZING": "badge-init"
    }.get(status, "badge-init")

    with kpi1:
        st.markdown(f"**Operational Status**")
        st.markdown(f"<span class='{status_color}' style='font-size: 22px;'>● {status}</span>", unsafe_allow_html=True)
        st.caption(f"Buffer Fill: {pred['buffer_fill_pct']}%")

    with kpi2:
        st.metric(label="Health Index", value=f"{health:.1f}%", delta=f"{health - 100:.1f}%" if health < 100 else "Optimal")

    with kpi3:
        st.metric(
            label="Risk Score (Smooth)",
            value=f"{risk:.4f}",
            delta=f"Threshold: 0.3691 (Crit)" if risk > 0.3 else "Normal Range"
        )
        st.caption(f"Debounce Active: **{pers} mins** (ISA-18.2)")

    with kpi4:
        st.metric(label="Inference Latency", value=f"{lat:.2f} ms")
        st.caption(f"Mode: {mode_str}")

    st.markdown("---")

    # 2. Main Analytics & Explainability Row
    row1_col1, row1_col2 = st.columns([6, 4])

    with row1_col1:
        st.subheader("📊 Multi-Sensor Contribution Matrix")
        contribs = pred.get("sensor_contributions_pct")
        if contribs:
            c_df = pd.DataFrame(list(contribs.items()), columns=["Sensor", "Contribution %"]).sort_values("Contribution %", ascending=True)
            st.bar_chart(c_df.set_index("Sensor"), horizontal=True, color="#d97706" if status=="WARNING" else "#dc2626")
        else:
            st.info("System is in baseline state. Sensor contributions will plot when deviations exceed 1.5 sigma.")

        # Live Health Timeline
        if len(st.session_state.history) > 1:
            st.subheader("📈 Real-time Degradation & Health Trajectory")
            hist_df = pd.DataFrame(st.session_state.history)
            st.line_chart(hist_df.set_index("minute")[["health_index", "risk_score"]])

    with row1_col2:
        st.subheader("🔬 Engineering Diagnostic Summary")
        summary = pred.get("attribution_summary")
        stagnation = pred.get("stagnation_alerts")

        if stagnation:
            st.error(f"⚠️ **SENSOR DECOUPLING / FLATLINE DETECTED!**")
            for sa in stagnation:
                st.markdown(f"- **{sa['sensor_name']}** ({sa['sensor_id']}): Variance collapsed to 0.0.")
            st.caption("Event 5 Safety Guard triggered. Physical wiring or transducer replacement required.")

        if summary:
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="margin-top:0;">{summary.get('fault_category', '')}</h4>
                <p><b>Hypothesis:</b> {summary.get('hypothesis_title', '')}</p>
                <p><b>Rationale:</b> {summary.get('engineering_rationale', '')}</p>
                <p><b>Primary Sensor:</b> <code>{pred.get('attributed_sensor', '')}</code> ({summary.get('direction', '')})</p>
                <p><b>Recommended Action:</b> {summary.get('recommended_primary_action', '')}</p>
                <p><b>FMEA Reference:</b> <code>{summary.get('fmea_reference_file', '')}</code></p>
            </div>
            """, unsafe_allow_html=True)
        elif status == "INITIALIZING":
            st.warning("Causal warm-up in progress. Trend baselines will finalize after 61 minutes.")
        else:
            st.success("All mechanical, electrical, and hydraulic subsystems operating within nominal ISO/ANSI tolerances.")

    st.markdown("---")

    # 3. Work Order Generation & RAG Section
    tab_wo, tab_chat = st.tabs(["📝 Autonomous Work Order Generator", "💬 Technical AI Maintenance Copilot"])

    with tab_wo:
        col_wo_action, col_wo_view = st.columns([3, 7])

        with col_wo_action:
            st.markdown("#### Work Order Dispatch")
            st.caption("Automatically converts multi-sensor anomalies into a formal engineering work order referencing ISO/ANSI/FMEA standards.")
            
            can_generate = status in ("WARNING", "CRITICAL") or pred.get("stagnation_alerts")
            
            if st.button("⚡ Generate Work Order", type="primary", use_container_width=True, disabled=not can_generate):
                with st.spinner("Querying RAG Knowledge Base and compiling Work Order..."):
                    wo = call_work_order_api(pred)
                    st.session_state.active_work_order = wo
                    st.success("Work Order successfully compiled!")

            if not can_generate:
                st.caption("ℹ️ Available when pump status is WARNING, CRITICAL, or Sensor Decoupled.")

        with col_wo_view:
            wo_data = st.session_state.active_work_order
            if wo_data:
                st.markdown(f"""
                ### 📋 WORK ORDER: `{wo_data.get('work_order_id', 'WO-PENDING')}`
                **Asset:** Two-Stage Centrifugal Pump ({wo_data.get('pump_id', 'PUMP_001')})  
                **Urgency:** <span class="badge-critical">{wo_data.get('urgency', 'CRITICAL')}</span>  
                **Diagnosis:** {wo_data.get('failure_diagnosis', 'N/A')}  
                **Standards Reference:** `{wo_data.get('standards_reference', 'ISO 10816-3')}`  
                **Est. Downtime:** {wo_data.get('estimated_downtime_hours', 1.5)} Hours | **LLM Verified:** {wo_data.get('llm_generated', False)}
                """, unsafe_allow_html=True)

                st.markdown("#### 🔒 LOTO Isolation Steps:")
                for step in wo_data.get("loto_safety_steps", []):
                    st.markdown(f"- {step}")

                st.markdown("#### 🔍 Inspection Checklist:")
                for check in wo_data.get("inspection_checklist", []):
                    st.markdown(f"- [ ] {check}")

                st.markdown("#### 🧰 Required Parts & Equipment:")
                for part in wo_data.get("required_parts_and_tools", []):
                    st.markdown(f"- 🔧 {part}")

                st.download_button(
                    label="📥 Export Work Order (JSON)",
                    data=json.dumps(wo_data, indent=2),
                    file_name=f"{wo_data.get('work_order_id', 'work_order')}.json",
                    mime="application/json"
                )
            else:
                st.info("No active work order. Trigger an anomaly preset and click 'Generate Work Order'.")

    with tab_chat:
        st.markdown("#### 💬 Ask AgriPulse Copilot")
        st.caption("Directly consult the RAG Assistant with live pump telemetry context and ISO 10816-3 manuals.")

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("e.g. What is the allowable radial vibration limit for this pump under ISO 10816-3?")
        if user_input:
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("Consulting pump documentation and live diagnostics..."):
                    reply = call_ai_chat_api(user_input, pred)
                    st.markdown(reply)
                    st.session_state.chat_messages.append({"role": "assistant", "content": reply})

# Footer
st.markdown("---")
st.caption("AgriPulse v3.0 • Two-Stage Centrifugal Pumping System • Industrial Predictive Maintenance & RAG Platform")
