# AgriPulse — Predictive Maintenance & Diagnostic AI Service

[![System Status](https://img.shields.io/badge/Service-Production--Ready-059669?style=flat-square)](#)
[![Machine Standard](https://img.shields.io/badge/Standard-ISO%2010816--3%20Class%20II-0284c7?style=flat-square)](#)
[![Deployment](https://img.shields.io/badge/Deployment-Railway%20Ready-7c3aed?style=flat-square)](#)
[![Target Asset](https://img.shields.io/badge/Asset-Centrifugal%20Irrigation%20Pump-d97706?style=flat-square)](#)

> **AgriPulse** is an industrial-grade AI microservice for continuous health assessment and early failure prediction on **Horizontal End-Suction Centrifugal Irrigation Pumps** (Grundfos NB / Kirloskar DB Series).
>
> It combines **ExtraTrees Causal Anomaly Detection** with a **Physics-Informed Multi-Sensor Diagnostic Engine (ISO 10816-3)** to alert operators **46 to 70 minutes** prior to functional trip.

---

## 1. Validated Industrial Benchmark Metrics

Evaluated on an untouched **Blind Test Set (July–August)** conforming strictly to industrial condition monitoring standards:

| Benchmark Metric | Validated Score | Industrial Significance |
| :--- | :---: | :--- |
| **Event 6 Early Warning Lead Time** | **46.0 minutes** | Detection of coupling misalignment before motor trip. |
| **Event 7 Early Warning Lead Time** | **70.0 minutes** | Early detection of hydraulic cavitation & bearing unbalance. |
| **Blind Test ROC-AUC** | **0.8878 (~89%)** | Strong discrimination between normal operating noise and true failure trends. |
| **False Alarm Rate** | **74 warning episodes / 2 months** | ~1 warning every 20 operating hours; 0 unmanaged critical false trips (ANSI/ISA-18.2). |
| **Sensor Footprint** | **Core-7 Sensors (28 Causal Features)** | High fidelity monitoring with low hardware instrumentation cost. |

---

## 2. Core-7 Sensor Instrumentation & Mapping

```
       [ELECTRIC MOTOR]               [COUPLING]              [PUMP VOLUTE]
   +-----------------------+              ||              +-------------------+
   |                       |              ||              |     Impeller      |
   | [sensor_05 / 11]      |         [sensor_13]          |                   |====> Discharge Line
   | Motor Phase Currents  |      Coupling Vibration      |                   |      
   |                       |                              | [sensor_28]       |
   | [sensor_00]           |                              | Discharge Flow    |
   | Motor DE Bearing Vib  |                              +-------------------+
   |                       |                                        |
   | [sensor_40]           |                                        | Suction Line
   | Motor DE Bearing Temp |                                        v
   +-----------------------+
```

| Sensor ID | Mounting Location | Monitored Phenomenon | Governing Standard |
| :--- | :--- | :--- | :--- |
| **`sensor_00`** | Motor Drive-End (DE) Bearing | Radial Vibration Velocity (RMS mm/s) | **ISO 10816-3 Class II** (> 4.5 mm/s Warning) |
| **`sensor_04`** | Motor Output Shaft Collar | Rotational Shaft Speed (RPM) | Slip % against rated synchronous speed |
| **`sensor_05`** | Motor Feeder Cable (Phase A) | Current Draw (Amperes RMS) | **IEC 60034-1** Full Load Amperes (FLA) |
| **`sensor_11`** | Motor Feeder Cable (Phase B) | Phase Balance Current (Amperes) | **NEMA MG 1** Phase Imbalance (< 3%) |
| **`sensor_13`** | Flexible Coupling Guard | Axial Vibration Velocity (RMS mm/s) | **ISO 10816-3** Dynamic Axial Deflection |
| **`sensor_28`** | Discharge Flange Manifold | Hydraulic Flow Rate (L/min) | **ANSI/HI 9.6.1** Cavitation Margin |
| **`sensor_40`** | Bearing Housing Outer Surface | Bearing Temperature (°C) | SKF Limits (> 75°C Warning, > 85°C Critical) |

---

## 3. API Endpoints Contract

### Health Check: `GET /health`
Returns service availability, model load status, and active thresholds.

### Predict & Diagnose: `POST /predict`

#### Input Payload:
```json
{
  "pump_id": "PUMP_IRRIGATION_001",
  "timestamp": "2024-03-15T10:30:00Z",
  "sensor_00": 1.85,
  "sensor_04": 2940.0,
  "sensor_05": 14.8,
  "sensor_11": 14.7,
  "sensor_13": 5.42,
  "sensor_28": 185.0,
  "sensor_40": 48.6
}
```

#### Output Diagnostic Response:
```json
{
  "pump_id": "PUMP_IRRIGATION_001",
  "timestamp": "2024-03-15T10:30:00Z",
  "status": "CRITICAL",
  "health_index_pct": 43.0,
  "risk_score": 0.342,
  "smooth_risk_score": 0.318,
  "buffer_ready": true,
  "attributed_sensor": "sensor_13",
  "primary_diagnosis": {
    "fault_code": "COUPLING_MISALIGNMENT",
    "title": "Flexible Coupling Misalignment & Spider Wear",
    "subsystem": "Shaft & Coupling Assembly",
    "confidence_pct": 56.0,
    "iso_standard": "ISO 10816-3 Class II (Axial Vibration Severity > 4.5 mm/s)",
    "urgency": "CRITICAL"
  },
  "sensor_contributions_pct": {
    "sensor_13": 57.4,
    "sensor_00": 20.8,
    "sensor_40": 11.9
  },
  "recommended_spare_parts": [
    "Flexible elastomeric spider insert (Size 110)",
    "Stainless alignment shims (0.05 - 1.0 mm)"
  ],
  "required_inspection_tools": [
    "Laser shaft alignment system",
    "Dual dial indicator set",
    "Torque wrench"
  ]
}
```

---

## 4. Railway Cloud Deployment (Zero-Config)

This repository is pre-configured with `Dockerfile` and `railway.json`.

1. Go to [Railway.app](https://railway.app) and create a new project.
2. Select **"Deploy from GitHub repo"** and choose `tasneem33355/AgriPulse`.
3. Railway automatically detects the root `Dockerfile` and builds the service.
4. Your service will be live at `https://your-app.up.railway.app` with interactive docs at `/docs`.

---

## 5. Local Quickstart

```bash
# Clone
git clone https://github.com/tasneem33355/AgriPulse.git
cd AgriPulse

# Run with Python
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Or with Docker
docker build -t agripulse-service .
docker run -p 8000:8000 agripulse-service
```
