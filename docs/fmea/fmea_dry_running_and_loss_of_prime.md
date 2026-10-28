# FMEA Specification: Dry Running, Loss of Prime & Mechanical Seal Thermal Distress

> **Asset:** Two-Stage Centrifugal Pumping System (Municipal & Irrigation Telemetry Archive)
> **Standard:** ANSI/HI 9.6.3 (Centrifugal Pump Operating Regions) & ISO 21049 / API 682 (Pumps - Shaft Sealing Systems)
> **Primary Sensor Indicator:** `sensor_05` (Motor Current Depressed $\ll 40\%$ FLA), `sensor_40` (Bearing/Seal Housing Temperature Elevated), `sensor_04` (Speed Surge)

---

## 1. Failure Mode Overview
Centrifugal pumps rely strictly on the pumped liquid to lubricate internal casing wear rings, throttle bushings, and mechanical seal faces. **Dry running** occurs when the pump operates without liquid in the volute (loss of suction prime, air pocket ingestion, or depleted supply reservoir). Without fluid cooling, mechanical seal faces overheat within 60 to 90 seconds, causing thermal carbon blistering, silicon carbide thermal shock cracking, and catastrophic seal failure, followed by severe frictional binding of stage wear rings.

## 2. Root Causes
* Sump/intake canal water level dropping below the minimum submergence depth of the suction bell.
* Failure of suction check/foot valve causing complete drainage of the suction column during standstill.
* Operator starting pump without proper liquid priming or vent valve de-aeration.
* Severe suction line air vortexing or ruptured suction hose.

## 3. Physical Symptoms & Telemetry Fingerprint
* **`sensor_05` (Motor Current Draw):** Drastic collapse to no-load / uncoupled levels ($Z \le -2.0\sigma$, typically $< 35\text{A}$ compared to nominal $76\text{A}$).
* **`sensor_04` (Motor Shaft Speed):** Slight speed escalation ($Z \ge +1.0\sigma$) due to negligible hydraulic resistance and zero impeller torque slip.
* **`sensor_40` (Housing Temperature):** Rapid thermal accumulation ($Z \ge +1.5\sigma$) due to heat conduction from overheated mechanical seal faces.
* **Acoustics:** Distinct hollow whining or high-pitched screeching sound.

## 4. Maintenance Checklist & Work Order Protocol
1. **Immediate Action:** Shut down motor drive immediately to prevent galling between rotating impellers and stationary casing rings.
2. **Suction Sump Level:** Check raw water level in suction pit or canal. Ensure water level is at least 1.0 meter above foot valve strainer.
3. **Re-Priming Protocol:** Open top volute casing air vent cock; fill pump casing with water until steady, bubble-free water overflows from vent.
4. **Mechanical Seal Inspection:** Inspect seal gland for discoloration, burnt elastomer smell, or liquid dripping once re-primed. If dripping exceeds 10 drops/minute, mechanical seal cartridge must be replaced.
5. **Wear Ring Clearance Check:** Rotate shaft by hand. If rotational torque is uneven, inspect impeller wear rings for galling/scoring.

## 5. Recommended Spare Parts & Equipment
* Cartridge-type mechanical seal assembly (Silicon Carbide vs. Carbon faces, Viton O-rings).
* Suction foot valve with weighted rubber seal flapper.
* Liquid level float switch or ultrasonic level sensor for automatic low-water cutoff.
* High-temperature IR pyrometer.
