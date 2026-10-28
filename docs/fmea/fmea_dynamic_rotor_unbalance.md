# FMEA Specification: Dynamic Rotor Unbalance & Impeller Erosion

> **Asset:** Two-Stage Centrifugal Pumping System (Municipal & Irrigation Telemetry Archive)
> **Standard:** ISO 1940-1 (Mechanical Vibration - Balance Quality Requirements for Rotors) & ISO 10816-3 (Machine Vibration Severity)
> **Primary Sensor Indicator:** `sensor_00` (Radial DE Vibration Elevated at 1X RPM), `sensor_13` (Coupling Axial Vibration Stable/Low)

---

## 1. Failure Mode Overview
Dynamic rotor unbalance occurs when the mass centerline of the rotating assembly (motor rotor, pump shaft, and impellers) deviates from its geometric rotational axis. In two-stage water pumps, unbalance is primarily caused by non-uniform material loss on the impellers (sand/silt erosion), uneven sediment cakes inside closed impeller shrouds, or partial cavitation pitting on vane tips. This generates continuous, centrifugal radial forces proportional to the square of rotational speed ($F = m \cdot r \cdot \omega^2$), inducing heavy cyclic fatigue on motor and pump bearings.

## 2. Root Causes
* Uneven abrasive wear of bronze or cast-iron impeller shrouds from suspended sand particles in irrigation water.
* Partial breakage or cracking of an impeller vane edge due to pebble ingestion.
* Uneven sediment or lime accumulation inside closed impeller flow passages during seasonal shutdown.
* Loss or dislodgement of shaft collar balancing weights.

## 3. Physical Symptoms & Telemetry Fingerprint
* **`sensor_00` (Motor DE Radial Vibration):** Sharp elevation ($Z \ge +2.0\sigma$) strictly in the radial/horizontal plane, dominated by 1X fundamental rotational frequency (~10.5 Hz / 634 RPM).
* **`sensor_13` (Coupling Axial Vibration):** Remains relatively stable and low ($|Z| < 1.5\sigma$), differentiating pure unbalance from angular misalignment.
* **`sensor_05` (Current):** Minor rhythmic current modulation at 1X rotational frequency.

## 4. Maintenance Checklist & Work Order Protocol
1. **LOTO Safety:** Isolate electric feeder circuit breaker; apply Lockout/Tagout.
2. **Volute Inspection:** Unbolt upper half of split casing or pull back suction casing. Inspect stage 1 and stage 2 impellers.
3. **Debris Cleaning:** Thoroughly pressure-wash internal impeller passages to remove lodged sediment, scale, or plant fibers.
4. **Runout & Balance Measurement:**
   - Mount dial indicator on shaft extension; verify radial runout is $< 0.03\text{ mm}$.
   - Perform two-plane dynamic field balancing (ISO 1940-1 Grade G2.5) using vibration analyzer and trial weights.
5. **Impeller Replacement:** If impeller vane thickness has deteriorated non-uniformly by $> 15\%$, dynamic balancing cannot compensate; replace impeller.

## 5. Recommended Spare Parts & Equipment
* Replacement dynamic-balanced impeller pair (Stage 1 & Stage 2).
* Portable dynamic vibration field balancer with optical tachometer.
* Dial test indicator (0.01 mm resolution) with magnetic stand.
* Stainless steel balancing correction weights.
