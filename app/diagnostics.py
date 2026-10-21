"""
Industrial Multi-Variate Diagnostic & Statistical Attribution Engine
Target Asset: Two-Stage Centrifugal Pumping System (Municipal Telemetry Archive)

Implements:
1. Signed Directional Deviation Signatures (ELEVATED vs DEPRESSED combinations).
2. Sensor Stagnation & Decoupling Detector (detecting flatline / zero-variance hardware faults like Event 5).
3. Relative Sensor Contribution Matrix for Dashboard Visualization.
4. RAG-Ready Context Payloads conforming to Industrial FMEA standards.
"""

from typing import Dict, Any, List, Optional
import numpy as np

# Verified IBM Telemetry Metadata & Physical Roles
SENSOR_ROLES = {
    "sensor_00": {
        "name": "Motor Drive-End Casing Radial Vibration",
        "subsystem": "Motor Drive-End Bearing Assembly",
        "nominal_range": (1.1, 2.5),
        "fmea_ref": "fmea_centrifugal_pump_bearings.md"
    },
    "sensor_04": {
        "name": "Motor Shaft Rotational Speed",
        "subsystem": "Drive Shaft & Motor Rotor",
        "nominal_range": (625.0, 645.0),
        "fmea_ref": "fmea_motor_overload_and_electrical.md"
    },
    "sensor_05": {
        "name": "Motor Stator Current Draw",
        "subsystem": "Motor Stator & Electrical Feed",
        "nominal_range": (70.0, 82.0),
        "fmea_ref": "fmea_motor_overload_and_electrical.md"
    },
    "sensor_11": {
        "name": "Motor Secondary Current Tap",
        "subsystem": "Electrical Feed Circuit",
        "nominal_range": (44.0, 56.0),
        "fmea_ref": "fmea_motor_overload_and_electrical.md"
    },
    "sensor_13": {
        "name": "Coupling Guard Vibration Velocity",
        "subsystem": "Flexible Shaft Coupling Assembly",
        "nominal_range": (1.4, 3.2),
        "fmea_ref": "fmea_coupling_misalignment_and_wear.md"
    },
    "sensor_28": {
        "name": "Stage-2 Impeller Rotational Speed",
        "subsystem": "Second-Stage Hydraulic Volute",
        "nominal_range": (1020.0, 1080.0),
        "fmea_ref": "fmea_hydraulic_cavitation_and_clogging.md"
    },
    "sensor_40": {
        "name": "Thrust Bearing Temperature",
        "subsystem": "Thrust Bearing Housing & Lubrication",
        "nominal_range": (45.0, 65.0),
        "fmea_ref": "fmea_centrifugal_pump_bearings.md"
    }
}

class IndustrialDiagnosticEngine:
    """
    Directional Multi-Variate Diagnostic Engine.
    Correlates signed sensor deviations and hardware decoupling states.
    """

    def __init__(self, roles: Dict[str, Any] = SENSOR_ROLES):
        self.roles = roles

    def check_sensor_stagnation(
        self,
        current_readings: Dict[str, float],
        sensor_rolling_stds: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detects sensor flatlining or decoupling (like Event 5 where variance collapsed).
        """
        decoupled_sensors = []
        if not sensor_rolling_stds:
            return decoupled_sensors

        for sensor, std_val in sensor_rolling_stds.items():
            curr_val = current_readings.get(sensor, 0.0)
            # A sensor is considered stagnated/dead if its rolling standard deviation is near-zero
            # while operating, or if its raw reading dropped to hard zero unexpectedly.
            if std_val < 1e-4 or (curr_val == 0.0 and sensor in ("sensor_04", "sensor_05", "sensor_28")):
                meta = self.roles.get(sensor, {})
                decoupled_sensors.append({
                    "sensor_id": sensor,
                    "sensor_name": meta.get("name", sensor),
                    "subsystem": meta.get("subsystem", "Instrumentation"),
                    "fault_code": "SENSOR_DECOUPLING_OR_FLATLINE",
                    "severity": "CRITICAL",
                    "description": f"Telemetry signal on {sensor} lost variance (std < 1e-4) or flatlined at zero. Indicates sensor line disconnect or transducer hardware failure (Event 5 signature)."
                })

        return decoupled_sensors

    def synthesize_diagnostic_hypothesis(
        self,
        signed_z: Dict[str, float],
        stagnated_alerts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Applies directional multi-sensor correlation rules to identify engineering hypotheses.
        """
        # If any sensor flatlined, this hardware fault takes precedence
        if stagnated_alerts:
            stagnant_s = stagnated_alerts[0]
            return {
                "fault_category": "HARDWARE_INSTRUMENTATION_FAULT",
                "subsystem": stagnant_s["subsystem"],
                "hypothesis_title": f"Telemetry Signal Flatline / Sensor Decoupling ({stagnant_s['sensor_id']})",
                "engineering_rationale": stagnant_s["description"],
                "fmea_document": "fmea_sensor_hardware_failure.md",
                "primary_action": f"Inspect electrical wiring and transducer mounting for {stagnant_s['sensor_id']} immediately."
            }

        z_13 = signed_z.get("sensor_13", 0.0)
        z_00 = signed_z.get("sensor_00", 0.0)
        z_05 = signed_z.get("sensor_05", 0.0)
        z_04 = signed_z.get("sensor_04", 0.0)
        z_28 = signed_z.get("sensor_28", 0.0)
        z_40 = signed_z.get("sensor_40", 0.0)

        # Rule 1: Coupling Misalignment & Excessive Axial Deflection
        if z_13 > 2.0:
            if z_00 > 1.5:
                rationale = "Severe axial vibration on coupling guard accompanied by correlated radial vibration transmission across the motor drive-end bearing."
            else:
                rationale = "Localized axial vibration surge across coupling hub indicating elastomeric spider insert wear or dynamic misalignment."
            return {
                "fault_category": "MECHANICAL_COUPLING_ALIGNMENT",
                "subsystem": "Flexible Shaft Coupling Assembly",
                "hypothesis_title": "Coupling Angular/Parallel Misalignment or Spider Element Degradation",
                "engineering_rationale": rationale,
                "fmea_document": "fmea_coupling_misalignment_and_wear.md",
                "primary_action": "Check coupling gap runout with dial indicator and inspect polyurethane spider insert for shredding."
            }

        # Rule 2: Motor Mechanical Overload & Hydraulic Impeller Drag
        if z_05 > 2.0 and z_28 < -1.5:
            return {
                "fault_category": "ELECTRICAL_HYDRAULIC_BINDING",
                "subsystem": "Second-Stage Hydraulic Volute",
                "hypothesis_title": "Hydraulic Binding, Silt Clogging, or Excessive Impeller Friction",
                "engineering_rationale": f"Motor current elevated (+{z_05:.1f} sigma) while stage-2 impeller rotational speed depressed ({z_28:.1f} sigma), indicating mechanical drag inside volute.",
                "fmea_document": "fmea_motor_overload_and_electrical.md",
                "primary_action": "Check pump suction strainer for weed/silt blockage; turn shaft by hand to check for binding."
            }

        # Rule 3: Bearing Lubrication Breakdown & Thermal Friction
        if z_40 > 2.0 and abs(z_00) < 2.0:
            return {
                "fault_category": "BEARING_LUBRICATION_STARVATION",
                "subsystem": "Thrust Bearing Housing",
                "hypothesis_title": "Thrust Bearing Lubrication Breakdown / Early Thermal Distress",
                "engineering_rationale": f"Bearing temperature elevated (+{z_40:.1f} sigma) prior to severe high-frequency vibration spike, indicating lubricant oxidation or lack of grease.",
                "fmea_document": "fmea_centrifugal_pump_bearings.md",
                "primary_action": "Verify bearing grease cavity level; check for seal leakage spraying into bearing housing."
            }

        # Rule 4: Bearing Structural Fatigue (Raceway Spalling)
        if z_00 > 2.0:
            return {
                "fault_category": "BEARING_MECHANICAL_FATIGUE",
                "subsystem": "Motor Drive-End Bearing",
                "hypothesis_title": "Bearing Raceway Flaking, Ball Fatigue, or Dynamic Rotor Unbalance",
                "engineering_rationale": f"High-frequency radial vibration elevated (+{z_00:.1f} sigma) on drive-end bearing casing.",
                "fmea_document": "fmea_centrifugal_pump_bearings.md",
                "primary_action": "Measure vibration envelope acceleration (RMS mm/s) and inspect bearing clearances."
            }

        # Fallback General Statistical Anomaly
        primary_sensor = max(signed_z, key=lambda s: abs(signed_z.get(s, 0.0)))
        meta = self.roles.get(primary_sensor, {})
        direction = "ELEVATED" if signed_z[primary_sensor] > 0 else "DEPRESSED"

        return {
            "fault_category": "GENERAL_PROCESS_DEVIATION",
            "subsystem": meta.get("subsystem", "General Pumping Train"),
            "hypothesis_title": f"Telemetry Anomaly on {meta.get('name', primary_sensor)} ({direction})",
            "engineering_rationale": f"Significant deviation ({signed_z[primary_sensor]:.1f} sigma) observed against rolling baseline.",
            "fmea_document": meta.get("fmea_ref", "fmea_general.md"),
            "primary_action": f"Inspect operating parameters associated with {primary_sensor}."
        }

    def attribute_anomaly(
        self,
        signed_z_scores: Dict[str, float],
        alert_status: str,
        risk_score: float,
        health_index_pct: float,
        current_readings: Optional[Dict[str, float]] = None,
        sensor_rolling_stds: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Executes complete multi-variate diagnostic pipeline.
        """
        if not signed_z_scores:
            return {
                "attributed_sensor": "UNKNOWN",
                "attribution_summary": None,
                "sensor_contributions_pct": {},
                "ranked_anomalies": [],
                "stagnation_warnings": []
            }

        # 1. Check for Hardware Flatlines / Sensor Decoupling
        stagnated_alerts = self.check_sensor_stagnation(
            current_readings=current_readings or {},
            sensor_rolling_stds=sensor_rolling_stds
        )

        # 2. Compute Relative Sensor Contributions for Dashboard Bar Chart
        magnitudes = {}
        for s, z in signed_z_scores.items():
            abs_z = abs(z)
            # Filter noise below 1.5 sigma
            magnitudes[s] = max(0.0, abs_z - 1.5) if abs_z > 1.5 else 0.0

        total_mag = sum(magnitudes.values())
        if total_mag > 1e-4:
            contributions = {s: round((mag / total_mag) * 100.0, 1) for s, mag in magnitudes.items()}
        else:
            contributions = {s: round(100.0 / len(signed_z_scores), 1) for s in signed_z_scores}

        # 3. Synthesize Engineering Hypothesis
        hypothesis_data = self.synthesize_diagnostic_hypothesis(signed_z_scores, stagnated_alerts)

        # 4. Primary Attributed Sensor
        if stagnated_alerts:
            primary_sensor = stagnated_alerts[0]["sensor_id"]
        else:
            primary_sensor = max(signed_z_scores, key=lambda s: abs(signed_z_scores.get(s, 0.0)))

        primary_z = signed_z_scores.get(primary_sensor, 0.0)
        direction = "ELEVATED" if primary_z >= 0 else "DEPRESSED"

        summary = {
            "attributed_sensor": primary_sensor,
            "sensor_name": self.roles.get(primary_sensor, {}).get("name", primary_sensor),
            "subsystem": hypothesis_data["subsystem"],
            "direction": direction,
            "deviation_z_score": round(float(primary_z), 2),
            "fault_category": hypothesis_data["fault_category"],
            "hypothesis_title": hypothesis_data["hypothesis_title"],
            "engineering_rationale": hypothesis_data["engineering_rationale"],
            "fmea_reference_file": hypothesis_data["fmea_document"],
            "recommended_primary_action": hypothesis_data["primary_action"],
            "methodology_note": "Multi-sensor directional heuristic based on 60-min baseline deviation; serves as explainable hypothesis for RAG work orders.",
            "urgency": "CRITICAL" if alert_status == "CRITICAL" else "HIGH"
        }

        # 5. Ranked Anomaly Contributors
        ranked_list = []
        for s in sorted(signed_z_scores.keys(), key=lambda k: abs(signed_z_scores[k]), reverse=True):
            z_val = signed_z_scores[s]
            s_meta = self.roles.get(s, {})
            dir_str = "ELEVATED" if z_val >= 0 else "DEPRESSED"
            ranked_list.append({
                "sensor_id": s,
                "sensor_name": s_meta.get("name", s),
                "subsystem": s_meta.get("subsystem", "Assembly"),
                "deviation_direction": dir_str,
                "z_score": round(float(z_val), 2),
                "contribution_pct": contributions.get(s, 0.0),
                "fmea_reference": s_meta.get("fmea_ref", "fmea_general.md")
            })

        return {
            "attributed_sensor": primary_sensor,
            "attribution_summary": summary,
            "sensor_contributions_pct": contributions,
            "ranked_anomalies": ranked_list,
            "stagnation_warnings": stagnated_alerts
        }

pump_diagnostics = IndustrialDiagnosticEngine()
