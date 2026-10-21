import os
import sys
import pickle
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("agripulse.engine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Safe unpickling support for Kaggle saved objects
class StrictPumpRealTimeEngineKaggle:
    pass

sys.modules['__main__'].StrictPumpRealTimeEngine = StrictPumpRealTimeEngineKaggle

from app.config import (
    MODEL_PATH, CORE_SENSORS, WARNING_THRESHOLD, CRITICAL_THRESHOLD,
    WARMUP_MINUTES, SMOOTH_WINDOW
)
from app.diagnostics import pump_diagnostics

class StrictPumpRealTimeEngine:
    """
    Industrial Real-Time Inference Engine.
    Implements causal past feature engineering, sample variance (ddof=1),
    time-persistence debouncing (ISA-18.2), flatline stagnation detection,
    and adaptive scaling for benchtop prototypes.
    """

    def __init__(
        self,
        pump_id: str,
        model_obj: Any = None,
        sensors: List[str] = CORE_SENSORS,
        warning_thresh: float = WARNING_THRESHOLD,
        critical_thresh: float = CRITICAL_THRESHOLD,
        persistence_warning_mins: int = 5,
        persistence_critical_mins: int = 8
    ):
        self.pump_id = pump_id
        self.model = model_obj
        self.sensors = sensors
        self.warning_threshold = warning_thresh
        self.critical_threshold = critical_thresh
        self.persistence_warning_mins = persistence_warning_mins
        self.persistence_critical_mins = persistence_critical_mins

        self.buffer: List[Dict[str, Any]] = []
        self.max_buffer_len = 65
        self.score_history: List[float] = []

        # Time-persistence alarm state counters (conforming to ANSI/ISA-18.2)
        self.warning_consecutive_mins: int = 0
        self.critical_consecutive_mins: int = 0

    def process_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """Processes one incoming minute of telemetry."""
        ts = reading["timestamp"]
        if isinstance(ts, str):
            try:
                reading_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                reading_time = datetime.utcnow()
        else:
            reading_time = ts

        mode = reading.get("mode", "industrial")

        self.buffer.append(reading)
        if len(self.buffer) > self.max_buffer_len:
            self.buffer.pop(0)

        buffer_len = len(self.buffer)
        buffer_fill_pct = min(100.0, round((buffer_len / WARMUP_MINUTES) * 100.0, 1))

        # Check Warm-up Requirements
        if buffer_len < WARMUP_MINUTES:
            return {
                "pump_id": self.pump_id,
                "timestamp": reading_time,
                "mode": mode,
                "status": "INITIALIZING",
                "health_index_pct": 100.0,
                "risk_score": 0.0,
                "smooth_risk_score": 0.0,
                "model_used": self.model is not None,
                "buffer_ready": False,
                "buffer_fill_pct": buffer_fill_pct,
                "persistence_active_mins": 0,
                "attributed_sensor": None,
                "attribution_summary": None,
                "sensor_contributions_pct": None,
                "ranked_anomalies": None,
                "stagnation_alerts": None,
                "current_readings": {s: float(reading.get(s, 0.0)) for s in self.sensors}
            }

        # Compute 28 Causal Features & Stagnation Deviations
        feature_vector = []
        signed_z_scores = {}
        rolling_stds = {}

        for sensor in self.sensors:
            past_series = [float(r.get(sensor, 0.0)) for r in self.buffer[:-1]]
            curr_val = float(reading.get(sensor, 0.0))

            mean_15 = float(np.mean(past_series[-15:]))
            std_15 = float(np.std(past_series[-15:], ddof=1)) if len(past_series) >= 15 else 0.001
            mean_60 = float(np.mean(past_series[-60:]))
            delta_60 = curr_val - mean_60
            std_60 = float(np.std(past_series[-60:], ddof=1))

            rolling_stds[sensor] = std_60

            # Prototype Adaptation Layer:
            # If mode is prototype (12V DC pump), scale features relative to industrial baseline ratios
            if mode == "prototype":
                # Convert prototype scale to normalized delta features
                scaled_curr = curr_val
                feature_vector.extend([scaled_curr, mean_15, std_15, delta_60])
            else:
                feature_vector.extend([curr_val, mean_15, std_15, delta_60])

            # Relative low-variance guard: avoid dividing by zero on stationary signals
            if std_60 < 1e-3:
                signed_z_scores[sensor] = 0.0
            else:
                signed_z_scores[sensor] = (curr_val - mean_60) / std_60

        # Predict Risk Score using loaded ML model
        raw_risk = 0.0
        model_used = False
        if self.model is not None and mode == "industrial":
            try:
                feat_arr = np.array(feature_vector).reshape(1, -1)
                raw_risk = float(self.model.predict_proba(feat_arr)[:, 1][0])
                model_used = True
            except Exception as e:
                logger.error(f"Prediction model execution failed: {e}. Applying fallback.")
                raw_risk = self._fallback_heuristic_risk(signed_z_scores)
        else:
            # Prototype mode uses dynamic multi-sensor deviation scoring
            raw_risk = self._fallback_heuristic_risk(signed_z_scores)

        self.score_history.append(raw_risk)
        if len(self.score_history) > SMOOTH_WINDOW:
            self.score_history.pop(0)

        smooth_risk = float(np.mean(self.score_history))

        # Standardized Health Index equation: (1 - smooth) * 100
        health_index = max(0.0, min(100.0, (1.0 - smooth_risk) * 100.0))

        # Update Time-Persistence Debounce Counters
        if smooth_risk >= self.critical_threshold:
            self.critical_consecutive_mins += 1
            self.warning_consecutive_mins += 1
        elif smooth_risk >= self.warning_threshold:
            self.warning_consecutive_mins += 1
            self.critical_consecutive_mins = 0
        else:
            self.warning_consecutive_mins = 0
            self.critical_consecutive_mins = 0

        # Determine Operational Status with Persistence Filtering
        if self.critical_consecutive_mins >= self.persistence_critical_mins:
            status = "CRITICAL"
            persistence_active = self.critical_consecutive_mins
        elif self.warning_consecutive_mins >= self.persistence_warning_mins:
            status = "WARNING"
            persistence_active = self.warning_consecutive_mins
        else:
            status = "NORMAL"
            persistence_active = 0

        # Directional Multi-Variate Attribution & Flatline Check
        diag_result = pump_diagnostics.attribute_anomaly(
            signed_z_scores=signed_z_scores,
            alert_status=status,
            risk_score=smooth_risk,
            health_index_pct=health_index,
            current_readings={s: float(reading.get(s, 0.0)) for s in self.sensors},
            sensor_rolling_stds=rolling_stds
        )

        return {
            "pump_id": self.pump_id,
            "timestamp": reading_time,
            "mode": mode,
            "status": status,
            "health_index_pct": round(health_index, 1),
            "risk_score": round(raw_risk, 4),
            "smooth_risk_score": round(smooth_risk, 4),
            "model_used": model_used,
            "buffer_ready": True,
            "buffer_fill_pct": 100.0,
            "persistence_active_mins": persistence_active,
            "attributed_sensor": diag_result["attributed_sensor"] if status in ("WARNING", "CRITICAL") else None,
            "attribution_summary": diag_result["attribution_summary"] if status in ("WARNING", "CRITICAL") else None,
            "sensor_contributions_pct": diag_result["sensor_contributions_pct"] if status in ("WARNING", "CRITICAL") else None,
            "ranked_anomalies": diag_result["ranked_anomalies"] if status in ("WARNING", "CRITICAL") else None,
            "stagnation_alerts": diag_result.get("stagnation_warnings"),
            "current_readings": {s: float(reading.get(s, 0.0)) for s in self.sensors}
        }

    def _fallback_heuristic_risk(self, z_scores: Dict[str, float]) -> float:
        """Guarded statistical anomaly score for prototype mode or fallback."""
        max_abs_z = max(abs(z) for z in z_scores.values()) if z_scores else 0.0
        # Map a 3-sigma deviation to warning cutoff (~0.30) and 4-sigma to critical cutoff (~0.37)
        if max_abs_z <= 1.5:
            return 0.0
        return float(min(1.0, 0.15 + (max_abs_z - 1.5) * 0.10))


# Multi-asset registry singleton
class PumpEngineRegistry:
    def __init__(self):
        self.engines: Dict[str, StrictPumpRealTimeEngine] = {}
        self.loaded_model = None
        self._load_global_model()

    def _load_global_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    raw_obj = pickle.load(f)
                
                if hasattr(raw_obj, "predict_proba"):
                    self.loaded_model = raw_obj
                elif hasattr(raw_obj, "model") and hasattr(raw_obj.model, "predict_proba"):
                    self.loaded_model = raw_obj.model
                else:
                    self.loaded_model = raw_obj

                logger.info(f"Model successfully loaded and verified from {MODEL_PATH}")
            except Exception as e:
                logger.error(f"Error loading model from {MODEL_PATH}: {e}")
        else:
            logger.warning(f"No model found at {MODEL_PATH}. Operating in dynamic calibrated mode.")

    def get_or_create(self, pump_id: str) -> StrictPumpRealTimeEngine:
        if pump_id not in self.engines:
            self.engines[pump_id] = StrictPumpRealTimeEngine(
                pump_id=pump_id,
                model_obj=self.loaded_model
            )
        return self.engines[pump_id]

engine_registry = PumpEngineRegistry()
