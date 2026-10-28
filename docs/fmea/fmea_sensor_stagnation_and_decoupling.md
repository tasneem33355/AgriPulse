# FMEA Specification: Telemetry Sensor Stagnation, Decoupling & Hardware Line Fault

> **Asset:** Two-Stage Centrifugal Pumping System (Municipal & Irrigation Telemetry Archive)
> **Standard:** ANSI/ISA-18.2 (Management of Alarm Systems for the Process Industries) & IEEE 1451 (Smart Transducer Interface for Sensors)
> **Primary Sensor Indicator:** Rolling 60-minute standard deviation collapses to near-zero ($\sigma_{60\text{m}} < 0.001$), or unexpected hard-zero reading while machine is energized (Event 5 Forensic Profile)

---

## 1. Failure Mode Overview
Telemetry instrumentation systems are exposed to continuous harsh field conditions including moisture, pipeline vibration, and thermal cycling. Sensor decoupling or stagnation occurs when an electronic transducer, signal cable, or analog-to-digital converter (ADC) channel fails silently. Unlike active mechanical degradation (which causes statistical variance to surge), sensor decoupling causes the signal to **flatline** (drop to absolute zero or freeze at a constant DC offset). Supervised ML models trained strictly on variance growth interpret this flatline as an ideal hyper-stable condition (causing catastrophic false negatives, as observed during historical Event 5).

## 2. Root Causes
* Mechanical vibration shearing or loosening the transducer mounting stud (accelerometer decoupling).
* Severed or corroded signal wiring harness (I2C SDA/SCL open circuit or 4-20mA current loop break).
* Water ingress into junction terminal boxes causing shorted sensor power supply rails.
* Cold solder joints or blown input channels on analog interface boards (ADS1115 / ESP32 ADC).

## 3. Physical Symptoms & Telemetry Fingerprint
* **Zero Variance Flatline:** Rolling 60-minute standard deviation drops below $0.001$ ($\sigma_{60\text{m}} < 1\text{e-4}$).
* **Hard Zero Drop:** Signal drops to exactly $0.0000$ and remains unmoving for $> 5$ consecutive minutes while adjacent machine channels show active operation.
* **Correlated Failure Check:** Motor current (`sensor_05`) or speed (`sensor_04`) indicates active running state while an individual channel is dead.

## 4. Maintenance Checklist & Work Order Protocol
1. **Visual Wiring Check:** Inspect the sensor wiring run from the transducer on the pump to the IoT gateway / marshalling box. Check for physical pinch points, melted insulation, or rodent damage.
2. **Terminal Integrity:** Tighten screw terminals on the analog/I2C breakout board. Clean any green copper oxide corrosion with contact cleaner.
3. **Loop Voltage Verification:** Measure DC excitation voltage at the sensor terminal block (typically $3.3\text{V}$ or $24\text{V DC}$). If voltage is zero, inspect power supply module fuse.
4. **Transducer Replacement & Re-Seating:**
   - Unthread damaged transducer.
   - Clean mounting pad down to bare metal; verify surface flatness.
   - Apply a thin layer of silicone grease to acoustic coupling interface.
   - Torque accelerometer mounting stud to manufacturer specification ($2.5 - 3.5\text{ Nm}$).
5. **Channel Self-Test:** Stream real-time telemetry into the gateway and verify signal dynamic variance resumes ($\sigma > 0.05$).

## 5. Recommended Spare Parts & Equipment
* Replacement 3-axis accelerometer module (ADXL345 or industrial IEPE accelerometer).
* Shielded twisted-pair telemetry cable (24 AWG, 2-pair with drain wire).
* Digital multimeter with frequency and micro-amp measurement.
* Electronic contact cleaner spray and heat-shrink tubing.
