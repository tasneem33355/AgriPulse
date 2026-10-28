# FMEA Specification: Motor Overload, Phase Imbalance & Impeller Clogging

> **Asset:** Two-Stage Centrifugal Pumping System (Municipal & Irrigation Telemetry Archive)
> **Standard:** IEC 60034-1 & NEMA MG 1-14.35 (Motors & Generators)
> **Primary Sensor Indicator:** `sensor_05` (Phase A Current), `sensor_11` (Phase B Current), `sensor_04` (Motor RPM)

---

## 1. Failure Mode Overview
Electric drive motors running two-stage centrifugal pumps operate close to full rated capacity. Mechanical obstruction within the pump stages (such as weeds, silt, or solid debris accumulation around the first or second stage impeller vanes) causes severe mechanical drag, forcing the motor to draw currents far above its Full Load Amperes (FLA). Prolonged overcurrent leads to thermal breakdown of stator winding insulation and catastrophic turn-to-turn short circuits.

## 2. Root Causes
* Ingestion of irrigation debris due to a torn or missing suction foot valve strainer basket.
* Severe scale or mineral build-up between impeller shrouds and casing wear rings.
* Supply grid voltage sag, loose electrical lugs, or blown utility fuses causing phase imbalance.

## 3. Physical Symptoms & Telemetry Fingerprint
* **`sensor_05` / `sensor_11` (Current Draw):** Current climbs above 115% nominal load.
* **Phase Imbalance:** Divergence between `sensor_05` and `sensor_11` exceeding 3% to 5%.
* **`sensor_04` (RPM):** Rotational speed decreases as slip percentage rises above normal baseline.
* **`sensor_28` (Stage 2 Speed):** Decoupling or drop in stage-2 speed despite high current draw.

## 4. Maintenance Checklist & Work Order Protocol
1. **Electrical Disconnect:** Trip main circuit breaker; apply Lockout/Tagout on motor control panel.
2. **Current Verification:** Use True-RMS AC clamp meter on motor leads to verify whether overcurrent is symmetrical (mechanical overload) or asymmetrical (electrical supply fault).
3. **Manual Hand Turn:** Uncouple or disengage motor drive; turn pump shaft by hand. Shaft must rotate freely and smoothly through 360 degrees without tight spots.
4. **Impeller Inspection:** If shaft is stiff, remove volute suction cover. Clear any fibrous weeds, sediment, or stones trapped inside the impeller eye.
5. **Insulation Resistance (Megger Test):** Apply 500V DC across stator windings to ground. Minimum allowable resistance: `> 5 Megaohms`.

## 5. Recommended Spare Parts & Equipment
* Suction strainer mesh basket (Stainless steel 304).
* Replacement volute casing gasket set.
* Motor thermal overload relay replacement.
* Digital AC True-RMS clamp meter.
* 500V/1000V DC Megohmmeter insulation resistance tester.
