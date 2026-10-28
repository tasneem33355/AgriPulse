# FMEA Specification: Flexible Shaft Coupling Misalignment & Spider Wear

> **Asset:** Two-Stage Centrifugal Pumping System (Municipal & Irrigation Telemetry Archive)
> **Standard:** ISO 10816-3 Class II & ANSI/HI 9.6.5 (Shaft Alignment Guidelines)
> **Primary Sensor Indicator:** `sensor_13` (Coupling Axial Vibration) + `sensor_00` (Motor DE Radial Vibration)

---

## 1. Failure Mode Overview
Shaft misalignment occurs when the geometric rotational centerlines of the driving electric motor and the driven two-stage centrifugal pump shaft are non-collinear (angular misalignment, parallel offset, or combined skew). This induces high-frequency dynamic bending moments and axial thrust loading across the flexible coupling hubs, causing severe wear or shredding of the elastomeric spider element.

## 2. Root Causes
* Foundation settling or thermal expansion differential between motor and pump casing.
* Loosened motor base hold-down bolts due to continuous hydraulic vibration.
* Degradation, hardening, or oil saturation of the polyurethane spider insert.
* Inaccurate initial cold alignment without accounting for pipe strain.

## 3. Physical Symptoms & Telemetry Fingerprint
* **`sensor_13` (Coupling Axial Vibration):** High 1X and 2X rotational speed axial vibration harmonics. RMS velocity exceeds 4.5 mm/s (ISO Zone C/D boundary).
* **`sensor_00` (Motor Bearing Vibration):** Secondary elevation due to vibration transmission across the shaft.
* **`sensor_04` (RPM):** Rotational speed remains generally nominal unless severe binding occurs.

## 4. Maintenance Checklist & Work Order Protocol
1. **LOTO Safety:** Isolate electric feeder breaker; apply Lockout/Tagout on motor starter.
2. **Coupling Guard Removal:** Unbolt safety guard; visually inspect for shredded black or red polyurethane dust.
3. **Elastomeric Insert Check:** Measure spider tooth thickness. Replace if tooth wear exceeds 1.5 mm or if elastomeric element shows heat embrittlement.
4. **Dial Indicator Alignment Check:** Mount dual dial indicators (Reverse Indicator Method) or use a laser alignment tool:
   - Radial parallel offset tolerance: `< 0.05 mm`.
   - Angular gap runout tolerance: `< 0.04 mm per 100 mm coupling hub diameter`.
5. **Shim Correction:** Insert pre-cut 304 stainless steel shims under motor feet as calculated.
6. **Retorque:** Torque baseplate bolts to specified torque (85 Nm for M12 Grade 8.8 bolts).

## 5. Recommended Spare Parts & Equipment
* Replacement elastomeric spider insert (Size per pump coupling model, Polyurethane / NBR).
* Stainless steel alignment shim pack (0.05 mm, 0.1 mm, 0.2 mm, 0.5 mm, 1.0 mm).
* Reverse dial indicator mounting bracket kit or Laser Alignment System.
* Calibrated torque wrench.
