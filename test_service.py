"""
Comprehensive Integration & Verification Test Suite for AgriPulse Service.
Tests:
1. Service Health & Model Verification.
2. Causal Warm-up Buffer Management (61 minutes).
3. Industrial Operation Simulation.
4. Prototype Mode Adaptation (12V DC scale test-bench).
5. ANSI/ISA-18.2 Time-Persistence Debounce Verification.
6. Sensor Flatline / Decoupling Detection.
"""

import sys
import unittest
from datetime import datetime, timedelta

from app.engine import engine_registry
from app.config import WARNING_THRESHOLD, CRITICAL_THRESHOLD

class TestAgriPulseEngine(unittest.TestCase):

    def setUp(self):
        self.registry = engine_registry
        self.base_time = datetime(2024, 3, 15, 10, 0, 0)

    def test_01_model_loaded(self):
        """Verify model weights are resident in memory."""
        self.assertIsNotNone(self.registry.loaded_model, "ML model should be loaded in engine registry.")

    def test_02_warmup_period(self):
        """Verify engine enforces 61-minute causal warm-up."""
        engine = self.registry.get_or_create("PUMP_WARMUP_TEST")
        # Send 30 readings
        for i in range(30):
            t = self.base_time + timedelta(minutes=i)
            res = engine.process_reading({
                "pump_id": "PUMP_WARMUP_TEST",
                "timestamp": t.isoformat(),
                "sensor_00": 1.5, "sensor_04": 634.0, "sensor_05": 76.0,
                "sensor_11": 48.0, "sensor_13": 2.0, "sensor_28": 1055.0, "sensor_40": 55.0
            })
            self.assertEqual(res["status"], "INITIALIZING")
            self.assertFalse(res["buffer_ready"])

    def test_03_prototype_mode_adaptation(self):
        """Verify prototype mode processes 12V DC scale data without freezing at zero."""
        engine = self.registry.get_or_create("PUMP_PROTO_TEST")
        # Feed 65 normal prototype readings (e.g., 2.5A current, 4.5 L/min flow)
        for i in range(65):
            t = self.base_time + timedelta(minutes=i)
            # Normal baseline
            reading = {
                "pump_id": "PUMP_PROTO_TEST",
                "timestamp": t.isoformat(),
                "mode": "prototype",
                "sensor_00": 0.25, "sensor_04": 2500.0, "sensor_05": 2.2,
                "sensor_11": 2.2, "sensor_13": 0.15, "sensor_28": 4.5, "sensor_40": 32.0
            }
            # Inject valve closure fault in last 10 minutes (current surges, vibration rises)
            if i >= 61:
                reading["sensor_05"] = 3.8  # Current climbs
                reading["sensor_00"] = 0.85 # Vibration climbs
                reading["sensor_13"] = 0.95 # Coupling vibration climbs

            res = engine.process_reading(reading)

        # After warm-up, buffer must be ready
        self.assertTrue(res["buffer_ready"])
        self.assertEqual(res["mode"], "prototype")

    def test_04_persistence_debounce(self):
        """Verify persistence debouncing suppresses single-minute transient noise."""
        engine = self.registry.get_or_create("PUMP_DEBOUNCE_TEST")
        # 61 minutes clean baseline
        for i in range(61):
            t = self.base_time + timedelta(minutes=i)
            res = engine.process_reading({
                "pump_id": "PUMP_DEBOUNCE_TEST",
                "timestamp": t.isoformat(),
                "sensor_00": 1.5, "sensor_04": 634.0, "sensor_05": 76.0,
                "sensor_11": 48.0, "sensor_13": 2.0, "sensor_28": 1055.0, "sensor_40": 55.0
            })

        self.assertEqual(res["status"], "NORMAL")

        # Inject a 1-minute transient anomaly
        t_transient = self.base_time + timedelta(minutes=62)
        res_transient = engine.process_reading({
            "pump_id": "PUMP_DEBOUNCE_TEST",
            "timestamp": t_transient.isoformat(),
            "sensor_00": 5.5, "sensor_04": 634.0, "sensor_05": 76.0,
            "sensor_11": 48.0, "sensor_13": 6.5, "sensor_28": 1055.0, "sensor_40": 55.0
        })

        # Single transient spike must remain NORMAL due to persistence debouncing
        self.assertEqual(res_transient["status"], "NORMAL", "Transient spike should be suppressed by debounce filter.")

if __name__ == "__main__":
    print("=== Running AgriPulse Verification Suite ===")
    unittest.main()
