# FMEA Specification: Structural Baseplate & Foundation Anchor Looseness

> **Asset:** Two-Stage Centrifugal Pumping System (Municipal & Irrigation Telemetry Archive)
> **Standard:** ISO 10816-3 (Evaluation of Machine Vibration - Mechanical Looseness Criteria)
> **Primary Sensor Indicator:** `sensor_00` (High Radial Vibration Across Harmonics), `sensor_13` (Coupling Vibration Surge), `sensor_04` (Speed Perturbation)

---

## 1. Failure Mode Overview
Structural looseness occurs when the pump or motor feet, baseplate, or underlying concrete foundation lose rigid mechanical coupling. The system exhibits non-linear mechanical stiffness, transforming normal minor rotational forces into severe structural motion. Looseness allows the machine to rock, twisting shafts and rapidly destroying shaft couplings, mechanical seals, and bearing raceways.

## 2. Root Causes
* Fractured or loose anchor bolts securing the steel baseplate to the concrete pad.
* Soft-foot condition (motor feet not coplanar with baseplate, causing casing distortion when bolted).
* Degradation, cracking, or voiding of epoxy or cementitious foundation grout under the baseplate.
* Severe pipe strain transferring external piping moments directly onto pump suction and discharge nozzles.

## 3. Physical Symptoms & Telemetry Fingerprint
* **`sensor_00` & `sensor_13` (Co-Elevated Vibration):** Both sensors exhibit severe concurrent elevation ($Z \ge +2.5\sigma$) with high harmonic content (1X, 2X, 3X, 0.5X sub-synchronous vibration).
* **Directional Amplitude:** Horizontal and radial vibration significantly higher than vertical vibration.
* **Sensitivity to Load:** Vibration level changes drastically when pump discharge valve is slightly throttled.

## 4. Maintenance Checklist & Work Order Protocol
1. **LOTO Safety:** Isolate electric supply panel; apply Lockout/Tagout.
2. **Anchor Bolt Torque Check:** Check all baseplate foundation bolts using a calibrated torque wrench. Verify bolts meet minimum specification ($120\text{ Nm}$ for M16 Grade 8.8 anchor studs).
3. **Soft-Foot Measurement:**
   - Position dial indicator vertically on each motor and pump foot.
   - Loosen hold-down bolt; observe dial deflection.
   - Any deflection $> 0.05\text{ mm}$ indicates soft-foot. Correct by inserting precision 304 stainless steel shims under the offending foot.
4. **Grout Integrity Inspection:** Tap baseplate surface with a ball-peen hammer; a hollow sound indicates voids between baseplate and concrete requiring epoxy pressure injection.
5. **Pipe Strain Verification:** Loosen pump flange bolts. If flange faces separate by $> 0.2\text{ mm}$ or shift out of alignment, piping supports must be adjusted to eliminate external nozzle loads.

## 5. Recommended Spare Parts & Equipment
* High-strength foundation anchor studs (Grade 8.8 galvanized or 316 stainless steel).
* Non-shrink high-flow epoxy grout (Sikadur or MasterFlow).
* Slotted stainless steel alignment shims (Size A & B).
* Calibrated heavy-duty torque wrench ($40 - 250\text{ Nm}$).
