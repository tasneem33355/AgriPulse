# AgriPulse — Predictive Maintenance & Diagnostic AI Service

[![System Status](https://img.shields.io/badge/Service-Production--Ready-059669?style=flat-square)](#)
[![Deployment](https://img.shields.io/badge/Deployment-Railway%20Ready-7c3aed?style=flat-square)](#)
[![Asset](https://img.shields.io/badge/Asset-Two--Stage%20Centrifugal%20Pump-d97706?style=flat-square)](#)

> **AgriPulse** is an industrial predictive maintenance microservice designed for continuous telemetry condition monitoring, advance trip prediction, and statistical anomaly attribution on **Two-Stage Centrifugal Water Pumping Systems** (Municipal & Irrigation Telemetry Archive).
>
> The service utilizes **Causal ExtraTrees Classification (Core-7 Channels, 28 past features)** combined with an **ANSI/ISA-18.2 Time-Persistence Debounce Engine** to alert operators up to **120 minutes** prior to functional trip.

---

## 1. Verified Industrial Benchmark & Honest Limitations

All evaluation metrics are computed on the untouched **Blind Test Period (July 1 – August 31, 2018)** following strict temporal walk-forward splitting:

| Evaluation Metric | Measured Score | Technical Interpretation |
| :--- | :---: | :--- |
| **Event 6 Early Warning Lead Time** | **46.0 minutes** | Detected prior to failure at Critical threshold (0.3691). |
| **Event 7 Early Warning Lead Time** | **70.0 minutes** | Detected > 1 hour prior to failure at Critical threshold (up to 120m at Warning). |
| **Target Warning Window** | **Up to 120.0 minutes** | Bounded strictly by the 120-minute pre-failure target definition. |
| **Blind Test ROC-AUC** | **0.8878 (~89%)** | Strong overall class separation between normal operation and true degradation. |
| **Average Precision (AP / PR-AUC)** | **0.0192** | Reflects the extreme operational class imbalance (~0.27% failure rows in test). |
| **Critical False Alarm Episodes** | **74 Episodes / 2 Months** | ~1.2 critical false alarms per operating day at raw 0.3691 cutoff without persistence filtering. |
| **Warning False Alarm Episodes** | **170 Episodes / 2 Months** | High recall threshold (0.3017) capturing minor transient surges. |
| **Operating Cutoffs** | **Warning: 0.3017 \| Critical: 0.3691** | Calibrated independently on clean June normal baseline operating percentiles (95% / 98.5%). |

---

## 2. Complete Walk-Forward Validation Results

Temporal cross-validation across all historical failure events reveals true operational capabilities and edge-case boundaries:

| Stage & Window | Target Event | Detected? | Lead Time | Stage ROC-AUC | Note / Failure Mode |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Stage 1 (April $\rightarrow$ May)** | Event 3 | **YES** | **120.0 min** | 0.8120 | Successful early detection at window boundary. |
| **Stage 1 (April $\rightarrow$ May)** | Event 4 | **YES** | **45.0 min** | 0.8120 | Clear pre-failure risk escalation. |
| **Stage 2 (May $\rightarrow$ June)** | Event 5 | **NO** | **0.0 min** | **0.0098** | **Known Edge Case:** Sensor decoupling/flatline failure where variance dropped to zero; model perceived it as hyper-stable. |
| **Stage 3 (June $\rightarrow$ Jul-Aug)** | Event 6 | **YES** | **46.0 min** | 0.8878 | Verified coupling anomaly trip. |
| **Stage 3 (June $\rightarrow$ Jul-Aug)** | Event 7 | **YES** | **70.0 min** | 0.8878 | Verified hydraulic/bearing degradation trip. |

---

## 3. Engineering Sensor Strategy & Selection

The repository architecture reflects findings from an empirical feature ablation study comparing three sensor groupings:
1. **All-50 Sensors:** Suffered from high-dimensional noise (curse of dimensionality); missed several event triggers.
2. **Prototype-5 Subset:** Lacked critical axial coupling and stage-2 impeller channels; produced zero lead-time triggers on historical industrial data.
3. **Core-7 Domain Group (Adopted):** Concentrates on primary mechanical/electrical stress points (`sensor_00`, `04`, `05`, `11`, `13`, `28`, `40`), achieving the best trade-off between detection sensitivity and feature robustness.

```
       [ELECTRIC MOTOR]               [COUPLING]              [TWO-STAGE VOLUTE]
   +-----------------------+              ||              +-------------------------+
   |                       |              ||              | Stage 1 | Stage 2       |
   | [sensor_05 / 11]      |         [sensor_13]          |         | Impeller      |
   | Motor Phase Currents  |      Coupling Vibration      |         | [sensor_28]   |
   |                       |                              |                         |
   | [sensor_00]           |                              +-------------------------+
   | Motor DE Bearing Vib  |                                           |
   |                       |                                           | Thrust Bearing
   | [sensor_04]           |                                           | [sensor_40]
   | Motor Shaft Speed     |                                           v
   +-----------------------+
```

| Sensor ID | Mechanical Subsystem | Dataset Telemetry Meaning | Typical Baseline Values |
| :--- | :--- | :--- | :--- |
| **`sensor_00`** | Motor Drive-End (DE) Bearing | Motor Casing Radial Vibration | ~1.4 to 2.5 |
| **`sensor_04`** | Motor Drive Shaft | Motor Rotational Speed (CPM/RPM) | ~630 to 640 |
| **`sensor_05`** | Motor Stator Feed Line | Motor Current Draw | ~70 to 80 |
| **`sensor_11`** | Motor Stator Secondary Tap | Secondary Current Tap | ~45 to 55 |
| **`sensor_13`** | Flexible Shaft Coupling | Coupling Vibration Velocity | ~1.5 to 3.2 |
| **`sensor_28`** | Second-Stage Impeller | Stage-2 Impeller Rotational Speed | ~1020 to 1080 CPM |
| **`sensor_40`** | Thrust Bearing Pedestal | Thrust Bearing Temperature | ~50 to 65 °C |

> **Hardware Prototype Note (Methodology Transfer):**  
> Physical test benches (such as our 12V DC benchtop rig) operate on miniature physical scales (e.g., 2A DC vs. 75A industrial motor current). The project proves the **IoT-to-Cloud Integration Pipeline** (sensor ingestion $\rightarrow$ streaming features $\rightarrow$ threshold debouncing $\rightarrow$ diagnostic attribution) rather than direct weight transfer.

---

## 4. Time-Persistence Alarm Filtering (ANSI/ISA-18.2)

To eliminate transient spikes and drastically reduce the 74 raw false alarm episodes, the engine implements a stateful **Debounce Filter**:
* **WARNING:** Requires risk score to remain above `0.3017` for **5 consecutive minutes**.
* **CRITICAL:** Requires risk score to remain above `0.3691` for **8 consecutive minutes**.
* Single-minute noise spikes are suppressed, preventing nuisance alarms in operational dashboards.

---

## 5. API Endpoints Contract

### Health Check: `GET /health`
Returns dynamic status (`HEALTHY` or `DEGRADED`), active tracking count, and operating cutoffs.

### Predict & Attribute: `POST /predict`
#### Sample Request Body:
```json
{
  "pump_id": "PUMP_IRRIGATION_001",
  "timestamp": "2024-03-15T10:30:00Z",
  "sensor_00": 2.45,
  "sensor_04": 634.0,
  "sensor_05": 76.5,
  "sensor_11": 48.2,
  "sensor_13": 5.42,
  "sensor_28": 1055.0,
  "sensor_40": 64.8
}
```

### AI Maintenance Assistant: `POST /ai/chat`
Interactive troubleshooting copilot combining live pump telemetry diagnosis with retrieved ISO 10816-3 & ANSI/HI standards.

### Autonomous Work Order Generator: `POST /ai/work-order`
Generates a formal, production-ready Maintenance Work Order JSON payload with LOTO isolation steps, inspection checklists, torque specifications, and required spare parts.

---

## 6. Cloud Deployment (Railway Ready)

Pre-configured with zero-config `Dockerfile` and `railway.json`:
1. Link repository to [Railway.app](https://railway.app).
2. Service auto-builds on Python 3.11 with pinned `scikit-learn==1.6.1`.
3. Interactive Swagger documentation is available live at `/docs`.
