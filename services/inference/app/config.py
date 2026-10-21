import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_PATH = os.getenv("CONFIG_PATH", str(BASE_DIR / "models" / "model_config.json"))
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "pump_engine_strict.pkl"))

# Load default config
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        MODEL_CONFIG = json.load(f)
else:
    MODEL_CONFIG = {
        "calibrated_thresholds": {
            "warning_threshold": 0.2713,
            "critical_threshold": 0.3169
        },
        "sensor_configuration": {
            "sensors_list": ["sensor_00", "sensor_04", "sensor_05", "sensor_11", "sensor_13", "sensor_28", "sensor_40"],
            "buffer_warmup_minutes": 61,
            "smoothing_window_minutes": 15
        }
    }

WARNING_THRESHOLD = float(os.getenv("WARNING_THRESHOLD", MODEL_CONFIG["calibrated_thresholds"]["warning_threshold"]))
CRITICAL_THRESHOLD = float(os.getenv("CRITICAL_THRESHOLD", MODEL_CONFIG["calibrated_thresholds"]["critical_threshold"]))
CORE_SENSORS = MODEL_CONFIG["sensor_configuration"]["sensors_list"]
WARMUP_MINUTES = int(MODEL_CONFIG["sensor_configuration"]["buffer_warmup_minutes"])
SMOOTH_WINDOW = int(MODEL_CONFIG["sensor_configuration"]["smoothing_window_minutes"])
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8002/generate-work-order")
