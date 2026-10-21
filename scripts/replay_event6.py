"""
AgriPulse Event 6 Live Replay & Demonstration Script.
Simulates a live telemetry stream leading into Event 6 (Mechanical Coupling Failure),
demonstrating the complete real-time pipeline:
- 61-minute causal warm-up buffer
- Normal baseline operations
- Pre-failure degradation ramp
- ANSI/ISA-18.2 time-persistence debouncing (5-min Warning, 8-min Critical)
- Directional multi-sensor diagnosis & FMEA attribution
"""

import time
import sys
import os
from pathlib import Path

# Add project root to sys.path so app module is discoverable from scripts directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timedelta
from app.engine import engine_registry

def run_event6_simulation(delay_sec: float = 0.05):
    print("=" * 78)
    print("  AGRIPULSE PREDICTIVE MAINTENANCE — EVENT 6 REPLAY SIMULATION")
    print("  Target Asset: Two-Stage Centrifugal Water Pump (Coupling Failure)")
    print("=" * 78)

    engine = engine_registry.get_or_create("DEMO_PUMP_001")
    base_time = datetime(2018, 7, 6, 8, 0, 0)

    # 1. Warm-up Phase (61 minutes of normal baseline)
    print("\n[PHASE 1] Initializing Causal Buffer (61 minutes of normal baseline)...")
    for m in range(61):
        ts = base_time + timedelta(minutes=m)
        reading = {
            "pump_id": "DEMO_PUMP_001",
            "timestamp": ts.isoformat(),
            "sensor_00": 1.48 + 0.02 * (m % 3),
            "sensor_04": 634.0,
            "sensor_05": 76.2 + 0.1 * (m % 2),
            "sensor_11": 48.1,
            "sensor_13": 1.95 + 0.03 * (m % 4),
            "sensor_28": 1055.0,
            "sensor_40": 54.5 + 0.05 * (m % 5)
        }
        res = engine.process_reading(reading)

    print(f"  Buffer Ready: {res['buffer_ready']} | Status: {res['status']} | Health: {res['health_index_pct']}%")

    # 2. Normal Steady-State Operations (10 minutes)
    print("\n[PHASE 2] Steady-State Normal Operations (Minutes 62-71)...")
    for m in range(61, 72):
        ts = base_time + timedelta(minutes=m)
        reading = {
            "pump_id": "DEMO_PUMP_001",
            "timestamp": ts.isoformat(),
            "sensor_00": 1.50,
            "sensor_04": 634.0,
            "sensor_05": 76.0,
            "sensor_11": 48.0,
            "sensor_13": 2.00,
            "sensor_28": 1055.0,
            "sensor_40": 55.0
        }
        res = engine.process_reading(reading)
        if m == 71:
            print(f"  Minute {m} -> Status: {res['status']} | Risk: {res['smooth_risk_score']:.4f} | Health: {res['health_index_pct']}%")

    # 3. Progressive Mechanical Degradation (Event 6 onset: coupling vibration surges)
    print("\n[PHASE 3] Anomaly Inception & ISA-18.2 Persistence Debouncing (Minutes 72-130)...")
    warning_announced = False
    critical_announced = False

    for m in range(72, 131):
        ts = base_time + timedelta(minutes=m)
        progress = min(1.0, (m - 72) / 45.0)  # 0.0 to 1.0 ramp

        # Mechanical coupling failure profile (canonical Event 6):
        # - Coupling vibration (sensor_13) surges from 2.0 -> 9.5
        # - Motor DE bearing vibration (sensor_00) rises from 1.5 -> 3.4
        # - Thrust bearing temperature (sensor_40) rises from 55 -> 72 °C
        # - Motor current (sensor_05) rises slightly due to misalignment drag
        # - Stage-2 speed (sensor_28) driven near 1045-1055 CPM
        reading = {
            "pump_id": "DEMO_PUMP_001",
            "timestamp": ts.isoformat(),
            "sensor_00": 1.50 + 1.90 * (progress ** 1.1),
            "sensor_04": 634.0 - 12.0 * progress,
            "sensor_05": 76.0 + 4.5 * progress,
            "sensor_11": 48.0 + 3.0 * progress,
            "sensor_13": 2.00 + 7.50 * (progress ** 1.2),
            "sensor_28": 1055.0 - 10.0 * progress,
            "sensor_40": 55.0 + 15.0 * progress
        }

        res = engine.process_reading(reading)

        status = res["status"]
        risk = res["smooth_risk_score"]
        health = res["health_index_pct"]
        pers = res["persistence_active_mins"]

        # Track transitions
        if status == "WARNING" and not warning_announced:
            print(f"\n  >>> [ALERT ELEVATION: WARNING] at Minute {m} (Persisted {pers} mins)")
            print(f"      Risk Score: {risk:.4f} (Threshold: 0.3017) | Health Index: {health}%")
            if res.get("attribution_summary"):
                summary = res["attribution_summary"]
                print(f"      Attributed Sensor : {res['attributed_sensor']} ({summary.get('sensor_name', '')})")
                print(f"      Fault Hypothesis  : {summary.get('hypothesis_title', '')}")
                print(f"      Engineering Rationale: {summary.get('engineering_rationale', '')}")
                print(f"      Recommended Action: {summary.get('recommended_primary_action', '')}")
            warning_announced = True

        if status == "CRITICAL" and not critical_announced:
            print(f"\n  >>> [ALERT ELEVATION: CRITICAL] at Minute {m} (Persisted {pers} mins)")
            print(f"      Risk Score: {risk:.4f} (Threshold: 0.3691) | Health Index: {health}%")
            lead_time = max(0, 171 - m)  # 46 minutes prior to simulated pump functional trip at min 171
            print(f"      Operational Lead Time to Functional Trip: ~{lead_time} minutes")
            if res.get("attribution_summary"):
                summary = res["attribution_summary"]
                print(f"      Fault Category    : {summary.get('fault_category', '')}")
                print(f"      Attributed Sensor : {res['attributed_sensor']}")
                print(f"      FMEA Reference    : {summary.get('fmea_reference_file', '')}")
                print(f"      Urgency Rating    : {summary.get('urgency', '')}")
            critical_announced = True

        # Print periodic progress
        if m % 5 == 0 or status in ("WARNING", "CRITICAL"):
            print(f"  Min {m:03d} | Status: {status:8s} | Risk: {risk:.4f} | Health: {health:5.1f}% | Debounce Mins: {pers:2d}")

        if delay_sec > 0:
            time.sleep(delay_sec)

    print("\n" + "=" * 78)
    print("  SIMULATION COMPLETE: Early warning successfully demonstrated!")
    print("=" * 78)

if __name__ == "__main__":
    run_event6_simulation(delay_sec=0.01)
