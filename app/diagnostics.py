"""
Physics-Informed Fault Diagnostics & Multi-Sensor Signature Engine
Target Asset: Horizontal End-Suction Centrifugal Irrigation Pump (ISO 10816-3 Class II)

Implements Multivariate Deviation Fingerprinting, Cosine Signature Similarity,
Confidence Scoring, and Root-Cause Sensor Contribution Breakdown for RAG & Dashboard.
"""

from typing import Dict, Any, List, Optional
import numpy as np

# Core 7 Sensors standard ordering
SENSORS_ORDER = [
    "sensor_00",  # Motor DE Bearing Radial Vibration
    "sensor_04",  # Motor Shaft RPM Speed
    "sensor_05",  # Motor Phase A Current
    "sensor_11",  # Motor Phase B Current
    "sensor_13",  # Coupling Axial Vibration
    "sensor_28",  # Discharge Flow Rate
    "sensor_40"   # Bearing Housing Surface Temperature
]

# Standard Engineering Signatures (Physics-Informed Benchmark Vectors)
# Represent expected relative Z-deviation weights [s00, s04, s05, s11, s13, s28, s40]
FAULT_SIGNATURE_PROFILES = {
    "COUPLING_MISALIGNMENT": {
        "title": "Flexible Coupling Misalignment & Spider Wear",
        "subsystem": "Shaft & Coupling Assembly",
        # Characterized by severe axial vibration (s13), high coupled motor vibration (s00), normal speed (s04)
        "signature_weights": np.array([0.5, 0.0, 0.1, 0.1, 1.0, 0.0, 0.2]),
        "iso_standard": "ISO 10816-3 Class II (Axial Vibration Severity > 4.5 mm/s)",
        "fmea_document": "fmea_coupling_misalignment_and_wear.md",
        "urgency": "HIGH",
        "recommended_parts": ["Flexible elastomeric spider insert (Size 110)", "Stainless alignment shims (0.05 - 1.0 mm)"],
        "recommended_tools": ["Laser shaft alignment system", "Dual dial indicator set", "Torque wrench"]
    },
    "BEARING_DEFECT_FATIGUE": {
        "title": "Drive-End Bearing Race Fatigue & Rolling Element Wear",
        "subsystem": "Motor DE Bearing Assembly",
        # High radial vibration (s00), elevated casing temp (s40), low current impact
        "signature_weights": np.array([1.0, 0.0, 0.1, 0.1, 0.3, 0.0, 0.6]),
        "iso_standard": "ISO 10816-3 & SKF Bearing Vibration Acceleration Envelope",
        "fmea_document": "fmea_centrifugal_pump_bearings.md",
        "urgency": "CRITICAL",
        "recommended_parts": ["Deep groove ball bearing (SKF 6308-2Z/C3)", "Bearing lock nut & seal ring"],
        "recommended_tools": ["Bearing induction heater", "Three-jaw mechanical puller", "FFT vibration spectrum analyzer"]
    },
    "BEARING_THERMAL_STARVATION": {
        "title": "Bearing Lubrication Starvation & Overheating",
        "subsystem": "Bearing Lubrication Chamber",
        # Primary signature is extreme thermal rise (s40), followed by secondary radial vibration (s00)
        "signature_weights": np.array([0.4, 0.0, 0.1, 0.1, 0.1, 0.0, 1.0]),
        "iso_standard": "SKF Thermal Guidelines: > 75°C Warning, > 85°C Critical (Grease breakdown)",
        "fmea_document": "fmea_centrifugal_pump_bearings.md",
        "urgency": "CRITICAL",
        "recommended_parts": ["High-temp polyurea synthetic grease (NLGI Grade 2)", "Grease nipple fitting"],
        "recommended_tools": ["Infrared pyrometer / thermal camera", "Contact thermocouple probe", "Grease dispensing gun"]
    },
    "MOTOR_OVERLOAD_CLOGGING": {
        "title": "Motor Overload & Impeller Mechanical Jamming",
        "subsystem": "Stator & Pump Volute Chamber",
        # High balanced phase currents (s05, s11), slight RPM slip drop (s04), flow drop (s28)
        "signature_weights": np.array([0.2, 0.4, 1.0, 1.0, 0.1, 0.5, 0.2]),
        "iso_standard": "IEC 60034-1 & NEMA MG 1 Continuous Full Load Allowances",
        "fmea_document": "fmea_motor_overload_and_electrical.md",
        "urgency": "HIGH",
        "recommended_parts": ["Suction inlet strainer basket", "Volute wear ring set", "Impeller retaining nut"],
        "recommended_tools": ["AC clamp ammeter", "Megohmmeter (500V DC insulation tester)", "Shaft turning bar"]
    },
    "CAVITATION_SUCTION_RESTRICTION": {
        "title": "Hydraulic Cavitation & Suction Line Restriction",
        "subsystem": "Hydraulic Volute & Discharge Line",
        # Severe flow drop (s28), motor current fluctuations (s05), random acoustic vibration spikes (s00)
        "signature_weights": np.array([0.4, 0.2, 0.5, 0.3, 0.2, 1.0, 0.0]),
        "iso_standard": "ANSI/HI 9.6.1 Centrifugal Pump NPSH Margin Guidelines",
        "fmea_document": "fmea_hydraulic_cavitation_and_clogging.md",
        "urgency": "HIGH",
        "recommended_parts": ["Suction flange gaskets", "Foot valve replacement flapper", "Mechanical seal cartridge"],
        "recommended_tools": ["Suction compound vacuum gauge", "Ultrasonic flow meter verification kit"]
    },
    "PHASE_IMBALANCE_ELECTRICAL": {
        "title": "Electrical Phase Asymmetry & Winding Unbalance",
        "subsystem": "Motor Terminal Box & Feeder Cable",
        # Severe discrepancy between phase A (s05) and phase B (s11)
        "signature_weights": np.array([0.1, 0.1, 0.9, 0.2, 0.0, 0.0, 0.3]),
        "iso_standard": "NEMA MG 1-14.35 Phase Current Unbalance Limit (< 3%)",
        "fmea_document": "fmea_motor_overload_and_electrical.md",
        "urgency": "CRITICAL",
        "recommended_parts": ["Thermal overload relay", "Feeder contactor terminals"],
        "recommended_tools": ["3-phase power analyzer", "Digital True-RMS multimeter"]
    }
}


class PhysicsInformedDiagnostics:
    """
    Combines localized empirical Z-deviations with domain physics signature matching
    to produce highly reliable, explainable fault diagnostics.
    """

    def __init__(self, profiles: Dict[str, Any] = FAULT_SIGNATURE_PROFILES):
        self.profiles = profiles
        self.sensors = SENSORS_ORDER

    def compute_sensor_contributions(self, z_deviations: Dict[str, float]) -> Dict[str, float]:
        """Calculates percentage contribution of each sensor to the current anomaly."""
        raw_magnitudes = {s: max(0.0, abs(z_deviations.get(s, 0.0))) for s in self.sensors}
        total = sum(raw_magnitudes.values())
        if total < 1e-6:
            return {s: round(100.0 / len(self.sensors), 2) for s in self.sensors}
        return {s: round((val / total) * 100.0, 1) for s, val in raw_magnitudes.items()}

    def diagnose_anomaly(
        self,
        z_deviations: Dict[str, float],
        alert_status: str,
        risk_score: float,
        health_index_pct: float,
        current_readings: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Executes Cosine Signature Matching against engineering profiles.
        Returns full diagnostic breakdown, confidence distribution, and dashboard payloads.
        """
        # Vectorize actual observed deviations
        obs_vec = np.array([max(0.0, abs(z_deviations.get(s, 0.0))) for s in self.sensors])
        norm_obs = np.linalg.norm(obs_vec)

        similarity_scores = {}
        for fault_key, profile in self.profiles.items():
            ref_vec = profile["signature_weights"]
            norm_ref = np.linalg.norm(ref_vec)
            if norm_obs < 1e-6 or norm_ref < 1e-6:
                similarity_scores[fault_key] = 0.0
            else:
                # Cosine similarity
                cosine_sim = float(np.dot(obs_vec, ref_vec) / (norm_obs * norm_ref))
                similarity_scores[fault_key] = max(0.0, cosine_sim)

        # Softmax confidence normalization
        score_values = np.array(list(similarity_scores.values()))
        if np.sum(score_values) > 0:
            exp_scores = np.exp(score_values * 3.0)  # Temperature scaling
            probabilities = exp_scores / np.sum(exp_scores)
            confidence_dist = {
                k: round(float(prob) * 100.0, 1)
                for k, prob in zip(similarity_scores.keys(), probabilities)
            }
        else:
            confidence_dist = {k: 0.0 for k in similarity_scores}

        # Select highest-confidence diagnosis
        top_fault_key = max(confidence_dist, key=confidence_dist.get)
        top_profile = self.profiles[top_fault_key]
        top_confidence = confidence_dist[top_fault_key]

        # Determine Primary Attributed Sensor
        attributed_sensor = max(z_deviations, key=lambda s: abs(z_deviations.get(s, 0.0)))
        sensor_contributions = self.compute_sensor_contributions(z_deviations)

        # Ranked list of possible causes for technician inspection
        ranked_causes = sorted(
            [
                {
                    "fault_code": k,
                    "fault_title": self.profiles[k]["title"],
                    "confidence_pct": confidence_dist[k],
                    "fmea_reference": self.profiles[k]["fmea_document"]
                }
                for k in confidence_dist
            ],
            key=lambda x: x["confidence_pct"],
            reverse=True
        )

        return {
            "status": alert_status,
            "risk_score": round(float(risk_score), 4),
            "health_index_pct": round(float(health_index_pct), 1),
            "attributed_sensor": attributed_sensor,
            "primary_diagnosis": {
                "fault_code": top_fault_key,
                "title": top_profile["title"],
                "subsystem": top_profile["subsystem"],
                "confidence_pct": top_confidence,
                "iso_standard": top_profile["iso_standard"],
                "fmea_document": top_profile["fmea_document"],
                "urgency": "CRITICAL" if alert_status == "CRITICAL" else top_profile["urgency"]
            },
            "sensor_contributions_pct": sensor_contributions,
            "differential_diagnostics": ranked_causes[:3],  # Top 3 differential options
            "recommended_spare_parts": top_profile["recommended_parts"],
            "required_inspection_tools": top_profile["recommended_tools"],
            "current_sensor_snapshot": current_readings or {}
        }


# Global diagnostic engine instance
pump_diagnostics = PhysicsInformedDiagnostics()

if __name__ == "__main__":
    import json

    # Test with typical Event 6 coupling failure pattern
    sample_z_scores = {
        "sensor_00": 2.1,  # Motor DE vibration elevated
        "sensor_04": 0.2,  # Normal RPM
        "sensor_05": 0.4,  # Normal current
        "sensor_11": 0.3,
        "sensor_13": 5.8,  # Huge coupling vibration spike!
        "sensor_28": 0.1,  # Normal flow
        "sensor_40": 1.2   # Slight temperature rise
    }

    result = pump_diagnostics.diagnose_anomaly(
        z_deviations=sample_z_scores,
        alert_status="CRITICAL",
        risk_score=0.342,
        health_index_pct=43.0,
        current_readings={"sensor_13": 5.42, "sensor_00": 2.85, "sensor_05": 16.2}
    )

    print("=== ADVANCED DIAGNOSTIC RESULT ===")
    print(json.dumps(result, indent=2))
