import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_PATH = os.getenv("CONFIG_PATH", str(BASE_DIR / "models" / "model_config.json"))
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "pump_engine_strict.pkl"))

# Load verified configuration
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        MODEL_CONFIG = json.load(f)
else:
    MODEL_CONFIG = {
        "calibrated_thresholds": {
            "warning_threshold": 0.3017,
            "critical_threshold": 0.3691
        },
        "sensor_configuration": {
            "sensors_list": ["sensor_00", "sensor_04", "sensor_05", "sensor_11", "sensor_13", "sensor_28", "sensor_40"]
        }
    }

cal_thresh = MODEL_CONFIG.get("calibrated_thresholds", {})
sensor_cfg = MODEL_CONFIG.get("sensor_configuration", {})

# Exact calibrated thresholds from June normal operating percentiles
WARNING_THRESHOLD = float(os.getenv("WARNING_THRESHOLD", cal_thresh.get("warning_threshold", 0.3017)))
CRITICAL_THRESHOLD = float(os.getenv("CRITICAL_THRESHOLD", cal_thresh.get("critical_threshold", 0.3691)))

CORE_SENSORS = sensor_cfg.get("sensors_list", ["sensor_00", "sensor_04", "sensor_05", "sensor_11", "sensor_13", "sensor_28", "sensor_40"])
WARMUP_MINUTES = int(sensor_cfg.get("buffer_warmup_minutes", 61))
SMOOTH_WINDOW = int(sensor_cfg.get("smoothing_window_minutes", 15))
