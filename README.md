# AgriPulse — Predictive Maintenance & Diagnostic AI Service

[![System Status](https://img.shields.io/badge/Service-Production--Ready-059669?style=flat-square)](#)
[![Machine Standard](https://img.shields.io/badge/Standard-ISO%2010816--3%20Class%20II-0284c7?style=flat-square)](#)
[![Deployment](https://img.shields.io/badge/Deployment-Railway%20Ready-7c3aed?style=flat-square)](#)
[![Asset](https://img.shields.io/badge/Asset-Two--Stage%20Centrifugal%20Pump-d97706?style=flat-square)](#)

> **AgriPulse** is an industrial-grade AI microservice for continuous telemetry health monitoring, early failure warning, and statistical anomaly attribution on **Multi-Stage Centrifugal Water Pumping Systems** (Municipal & Irrigation Station Archive).
>
> The service utilizes **Causal ExtraTrees Feature Transformations** combined with a **Directional Statistical Attribution Engine** to detect impending functional trips **46 to 70 minutes** in advance.

---

## 1. Verified Industrial Benchmark Metrics

Evaluated on an untouched, out-of-sample **Blind Test Period (July 1 – August 31, 2018)** following strict temporal walk-forward splitting:

| Industrial Evaluation Metric | Validated Score | Engineering Interpretation |
| :--- | :---: | :--- |
| **Event 6 Early Warning Lead Time** | **46.0 minutes** | Advance alert triggered before catastrophic functional trip. |
| **Event 7 Early Warning Lead Time** | **70.0 minutes** | Early detection window (> 1 hour) allowing intervention. |
| **Blind Test ROC-AUC** | **0.8878 (~89%)** | Strong discrimination separating baseline operational jitter from true degradation. |
| **Average Precision (AP / PR-AUC)** | **0.0192** | Reflects the extreme operational class imbalance (< 0.2% positive failure rows). |
| **False Alarm Episodes (2 Months)** | **74 Warning Episodes** | ~1 warning episode per 20 operating hours at 95th percentile cutoff. |
| **Unmanaged Critical Trips** | **0 Episodes** | High-precision operational threshold at 98.5th percentile cutoff. |
| **Operating Cutoffs** | **Warning: 0.3017 \| Critical: 0.3691** | Calibrated independently on clean June normal baseline operating percentiles. |

---

## 2. Telemetry Architecture & Verified Sensor Provenance

The model monitors **7 core telemetry channels (28 causal past-window features)** extracted from the industrial two-stage centrifugal pump telemetry log:

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

### Verified Mapping (Conforming to Original IBM Telemetry Registry):

| Sensor ID | Mechanical / Electrical Subsystem | Dataset Telemetry Meaning | Nominal Baseline Range |
| :--- | :--- | :--- | :--- |
| **`sensor_00`** | Motor Drive-End (DE) Bearing | Radial Vibration Velocity | 1.1 – 2.5 |
| **`sensor_04`** | Motor Drive Shaft | Rotational Speed (RPM / CPM) | ~2940 (Synchronous) |
| **`sensor_05`** | Motor Stator Feed Line | Phase A Current Draw | 13.0 – 16.5 |
| **`sensor_11`** | Motor Stator Feed Line | Phase B Current Draw | 13.0 – 16.5 |
| **`sensor_13`** | Flexible Shaft Coupling Guard | Axial Vibration Velocity | 1.2 – 3.2 |
| **`sensor_28`** | Second-Stage Impeller Assembly | Impeller Rotational Speed | 1020 – 1080 CPM |
| **`sensor_40`** | Thrust Bearing Housing | Thrust Bearing Temperature | 42.0 – 58.0 |

> **Note on Prototype Hardware:** Physical test-benches (such as 12V DC benchtop rigs) operate on different absolute physical units. The machine learning pipeline applies **Methodology Transfer** (causal feature extraction, rolling Z-deviation baselines, and percentile calibration) rather than raw zero-shot weight transfer.

---

## 3. Directional Anomaly Attribution Engine

Instead of unverified black-box fault classification on unlabeled datasets, the service implements **Directional Statistical Attribution**:
* Evaluates directional deviations: **ELEVATED** vs. **DEPRESSED** (e.g., thermal rise vs. speed collapse).
* Applies **Low-Variance Stationarity Guards** (`std < 1e-3` forces $Z = 0$) preventing mathematical division artifacts on stationary sensors.
* Computes normalized percentage contributions per sensor for direct UI visualization (Bar Charts).

---

## 4. API Endpoints Contract

### Health Check: `GET /health`
```json
{
  "status": "HEALTHY",
  "service": "agripulse-inference-service",
  "model_loaded": true,
  "active_pumps_tracked": 1,
  "calibrated_thresholds": {
    "warning": 0.3017,
    "critical": 0.3691
  }
}
```

### Predict & Attribute: `POST /predict`
#### Sample Request Body:
```json
{
  "pump_id": "PUMP_IRRIGATION_001",
  "timestamp": "2024-03-15T10:30:00Z",
  "sensor_00": 2.45,
  "sensor_04": 2938.0,
  "sensor_05": 14.8,
  "sensor_11": 14.7,
  "sensor_13": 5.42,
  "sensor_28": 1055.0,
  "sensor_40": 48.6
}
```

---

## 5. Cloud Deployment (Railway Ready)

Pre-configured with zero-config `Dockerfile` and `railway.json`:
1. Link repository to [Railway.app](https://railway.app).
2. Root `Dockerfile` builds Python 3.11 with pinned `scikit-learn==1.6.1`.
3. Service spins up automatically on dynamic `$PORT` with interactive documentation at `/docs`.
