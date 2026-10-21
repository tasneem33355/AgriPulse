# FMEA Specification: Hydraulic Cavitation & Suction Line Restriction

> **Asset:** Horizontal End-Suction Centrifugal Irrigation Pump
> **Standard:** ANSI/HI 9.6.1 (NPSH Margin & Suction Energy Limits)
> **Primary Sensor Indicator:** `sensor_28` (Flow Rate), `sensor_00` (Acoustic Vibration), `sensor_04` (RPM fluctuations)

---

## 1. Failure Mode Overview
Cavitation occurs when local static pressure inside the pump impeller eye drops below the vapor pressure of the pumped liquid ($P < P_v$). Vapor bubbles form in low-pressure zones and subsequently collapse violently as they enter higher-pressure volute regions. Micro-jets created by bubble collapse deliver localized impact pressures exceeding 1,000 MPa, pitting and eroding bronze or cast-iron impeller vanes, deteriorating hydraulic performance, and causing severe shock loading.

## 2. Root Causes
* Insufficient Net Positive Suction Head Available ($NPSH_A < NPSH_R + 0.5m$).
* Clogged suction foot valve, blocked pipe strainer, or excessively long suction lift (> 5 meters).
* Air ingestion through loose suction pipe flange joints or degraded shaft packing.
* Throttling the suction line valve instead of the discharge line valve.

## 3. Physical Symptoms & Telemetry Fingerprint
* **`sensor_28` (Flow Rate):** Sharp discharge flow rate collapse (drop of > 30% below Best Efficiency Point).
* **`sensor_00` (Acoustic / High-Frequency Vibration):** Erratic, wideband high-frequency noise resembling "pumping gravel or marbles".
* **`sensor_05` (Current):** Erratic current fluctuations due to hydraulic load instability.

## 4. Maintenance Checklist & Work Order Protocol
1. **Suction Head Check:** Read suction line compound vacuum gauge. Gauge vacuum must not exceed 0.4 bar (4 meters head).
2. **Foot Valve Inspection:** Pull suction pipe from intake canal/sump. Clear silt, mud, and organic growth blocking the foot valve flapper.
3. **Flange Joint Integrity:** Inspect all suction line rubber gaskets and clamp bolts for air leaks. Apply vacuum grease or silicone sealant across joints if air bubbling is suspected.
4. **Impeller Inspection:** Open volute casing; inspect leading edges of impeller vanes for characteristic "sponge-like" cavitation pitting or mechanical erosion. Replace impeller if blade thickness is reduced by more than 20%.

## 5. Recommended Spare Parts & Equipment
* Suction foot valve replacement (Cast iron flapper type, G2" or G3").
* Heavy-duty EPDM flange gaskets (Suction & Discharge).
* Replacement bronze/cast-iron centrifugal impeller.
* Bourdon tube compound vacuum gauge (-1.0 to +1.5 bar).
