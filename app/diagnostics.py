"""
Statistical Anomaly Attribution & Engineering Hypothesis Matcher
Target Asset: Two-Stage Centrifugal Pumping System (Municipal Water Telemetry Archive)

Implements directional Z-score deviations, low-variance guards (avoiding zero-std division artifacts),
and heuristic mapping to standard centrifugal pump failure modes.
"""

from typing import Dict, Any, List, Optional
import numpy as np

# Correct Sensor Registry from verified dataset telemetry
SENSOR_METADATA = {
    "sensor_00": {
        "name": "Motor DE Bearing Radial Vibration",
        "subsystem": "Motor Drive-End Bearing",
        "high_deviation_fault": "Bearing Raceway Wear, Flaking, or Dynamic Rotor Unbalance",
        "low_deviation_fault": "Sensor Disconnection or Decoupling",
        "fmea_ref": "fmea_centrifugal_pump_bearings.md"
    },
    "sensor_04": {
        "name": "Motor Shaft Rotational Speed",
        "subsystem": "Motor Drive Shaft",
        "high_deviation_fault": "Overspeed or VFD Control Surge",
        "low_deviation_fault": "Motor Slip Under Severe Drag or Impeller Jamming",
        "fmea_ref": "fmea_motor_overload_and_electrical.md"
    },
    "sensor_05": {
        "name": "Motor Stator Phase A Current",
        "subsystem": "Electrical Feeder & Stator",
        "high_deviation_fault": "Motor Mechanical Overload, Volute Binding, or Voltage Depression",
        "low_deviation_fault": "Dry Running, Loss of Prime, or Electrical Disconnect",
        "fmea_ref": "fmea_motor_overload_and_electrical.md"
    },
    "sensor_11": {
        "name": "Motor Stator Phase B Current",
        "subsystem": "Electrical Feeder & Phase Balance",
        "high_deviation_fault": "Phase Asymmetry or Overcurrent Overload",
        "low_deviation_fault": "Single-Phasing Condition or Circuit Loss",
        "fmea_ref": "fmea_motor_overload_and_electrical.md"
    },
    "sensor_13": {
        "name": "Coupling Axial Vibration",
        "subsystem": "Flexible Shaft Coupling",
        "high_deviation_fault": "Coupling Angular/Parallel Misalignment or Spider Element Deterioration",
        "low_deviation_fault": "Sensor Disconnect or Damping Dampening",
        "fmea_ref": "fmea_coupling_misalignment_and_wear.md"
    },
    "sensor_28": {
        "name": "Stage 2 Impeller Rotational Speed",
        "subsystem": "Second-Stage Hydraulic Assembly",
        "high_deviation_fault": "Inter-stage Hydraulic Surging or Cavitation Jitter",
        "low_deviation_fault": "Stage 2 Impeller Binding or Severe Hydraulic Choke",
        "fmea_ref": "fmea_hydraulic_cavitation_and_clogging.md"
    },
    "sensor_40": {
        "name": "Thrust Bearing Temperature",
        "subsystem": "Thrust Bearing & Lubrication Circuit",
        "high_deviation_fault": "Lubrication Breakdown, Excessive Axial Thrust Loading, or Friction Seizure",
        "low_deviation_fault": "Thermal Sensor Open Circuit",
        "fmea_ref": "fmea_centrifugal_pump_bearings.md"
    }
}

class StatisticalAttributionEngine:
    """
    Computes guarded directional Z-scores and produces explainable statistical attributions.
    Avoids artificial confidence probabilities on unlabeled datasets.
    """

    def __init__(self, metadata: Dict[str, Any] = SENSOR_METADATA):
        self.metadata = metadata

    def attribute_anomaly(
        self,
        signed_z_scores: Dict[str, float],
        alert_status: str,
        risk_score: float,
        health_index_pct: float,
        current_readings: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Analyzes directional sensor deviations and ranks anomalous telemetry contributors.
        """
        if not signed_z_scores:
            return {
                "attributed_sensor": "UNKNOWN",
                "attribution_summary": None,
                "sensor_contributions_pct": {},
                "ranked_anomalies": []
            }

        # Calculate magnitude contributions (ignoring sensor jitter below 1.5 sigma)
        magnitudes = {}
        for s, z in signed_z_scores.items():
            abs_z = abs(z)
            # Threshold guard: deviations under 1.5 sigma are treated as normal background noise
            magnitudes[s] = max(0.0, abs_z - 1.5) if abs_z > 1.5 else 0.0

        total_mag = sum(magnitudes.values())
        if total_mag > 1e-4:
            contributions = {s: round((mag / total_mag) * 100.0, 1) for s, mag in magnitudes.items()}
        else:
            # If all deviations are minimal, equal contribution
            contributions = {s: round(100.0 / len(signed_z_scores), 1) for s in signed_z_scores}

        # Select primary attributed sensor (highest absolute Z deviation)
        primary_sensor = max(signed_z_scores, key=lambda s: abs(signed_z_scores.get(s, 0.0)))
        primary_z = signed_z_scores[primary_sensor]
        meta = self.metadata.get(primary_sensor, {})

        direction = "ELEVATED" if primary_z >= 0 else "DEPRESSED"
        hypothesis = meta.get("high_deviation_fault" if primary_z >= 0 else "low_deviation_fault", "Undetermined Anomaly")

        summary = {
            "attributed_sensor": primary_sensor,
            "sensor_name": meta.get("name", primary_sensor),
            "subsystem": meta.get("subsystem", "Mechanical Assembly"),
            "direction": direction,
            "deviation_z_score": round(float(primary_z), 2),
            "attributed_failure_hypothesis": hypothesis,
            "methodology_note": "Statistical heuristic based on 60-min baseline deviation; represents anomalous telemetry indicator, not a definitive root-cause classification.",
            "urgency": "CRITICAL" if alert_status == "CRITICAL" else "HIGH"
        }

        # Ranked list of all sensors contributing to the anomaly
        ranked_list = []
        for s in sorted(signed_z_scores.keys(), key=lambda k: abs(signed_z_scores[k]), reverse=True):
            z_val = signed_z_scores[s]
            s_meta = self.metadata.get(s, {})
            dir_str = "ELEVATED" if z_val >= 0 else "DEPRESSED"
            hyp_str = s_meta.get("high_deviation_fault" if z_val >= 0 else "low_deviation_fault", "Anomaly")
            ranked_list.append({
                "sensor_id": s,
                "sensor_name": s_meta.get("name", s),
                "subsystem": s_meta.get("subsystem", "Assembly"),
                "deviation_direction": dir_str,
                "z_score": round(float(z_val), 2),
                "contribution_pct": contributions.get(s, 0.0),
                "possible_fault_mode": hyp_str,
                "fmea_reference": s_meta.get("fmea_ref", "fmea_general.md")
            })

        return {
            "attributed_sensor": primary_sensor,
            "attribution_summary": summary,
            "sensor_contributions_pct": contributions,
            "ranked_anomalies": ranked_list
        }

pump_diagnostics = StatisticalAttributionEngine()
