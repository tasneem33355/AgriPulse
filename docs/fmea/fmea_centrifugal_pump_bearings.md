# FMEA Specification: Drive-End Bearing Fatigue & Lubrication Starvation

> **Asset:** Two-Stage Centrifugal Pumping System (Municipal & Irrigation Telemetry Archive)
> **Standard:** ISO 10816-3 (Bearing Vibration Severity) & SKF General Operating Limits
> **Primary Sensor Indicator:** `sensor_00` (Motor DE Radial Vibration) & `sensor_40` (Thrust Bearing Housing Temperature)

---

## 1. Failure Mode Overview
Drive-End (DE) and Thrust bearings support heavy radial hydraulic loads from the pump impellers and dynamic shaft axial forces. Failure typically progresses through four distinct stages:
1. Subsurface micro-fissuring and lubricant film breakdown.
2. Spalling and flaking of raceways (inner/outer ring).
3. Cage pocket cracking and ball skidding.
4. Total rotational seizure / catastrophic locked rotor.

## 2. Root Causes
* Lubricant breakdown due to extended operating hours without regreasing.
* Over-greasing causing excessive churning friction and high internal temperatures.
* Ingress of pumped water or airborne dust through degraded labyrinth oil seals.
* Excessive mechanical unbalance or dynamic shaft misalignment.

## 3. Physical Symptoms & Telemetry Fingerprint
* **`sensor_00` (Motor Bearing Radial Vibration):** Spikes sharply in high-frequency acceleration bands (envelope velocity > 4.5 mm/s RMS).
* **`sensor_40` (Bearing Housing Surface Temp):** Climbs steadily above 75°C (Warning) or 85°C (Critical).
* **Audible Acoustics:** High-pitched grinding, chattering, or metallic squealing.

## 4. Maintenance Checklist & Work Order Protocol
1. **Initial Assessment:** Measure casing skin temperature with calibrated infrared pyrometer.
2. **Purge Check:** Open grease relief valve at bottom of bearing cap; inspect discharged grease:
   - If black/burnt: Lubricant has thermally oxidized.
   - If milky/opaque: Water moisture contamination detected.
3. **Regreasing:** If temperature is elevated but vibration is moderate, pump 15-20 grams of fresh Lithium Complex EP2 grease while shaft rotates slowly. Monitor temperature drop over 30 minutes.
4. **Bearing Replacement (If Vibration Exceeds 4.5 mm/s):**
   - Dismantle motor end-bell.
   - Use three-jaw mechanical puller or bearing induction heater for removal.
   - Fit new deep groove ball bearing heated uniformly to 110°C.
   - Replace nitrile rubber V-ring oil seals.

## 5. Recommended Spare Parts & Equipment
* Deep groove ball bearing / Angular contact thrust bearing (per asset specifications).
* High-temperature synthetic polyurea or Lithium EP2 grease.
* Replacement rubber shaft contact seal (V-Ring).
* Three-jaw mechanical puller and induction heater.
