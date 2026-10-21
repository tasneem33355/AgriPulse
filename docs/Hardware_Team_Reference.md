# Hardware Team Reference — Benchtop Pump Test Rig (ESP32)

> **Target Implementation:** Functional Scale Test Rig (12V DC Motor-Driven Pump Loop)
> **Role in Project:** Physical Proof-of-Concept for Real-Time IoT Telemetry & Fault Injection
> **Version:** 3.0 — Physical BOM Alignment
> **Audience:** Hardware & Embedded Systems Team

---

## 1. What the Hardware Test Rig Actually Does

The benchtop prototype is designed to demonstrate real-time physical telemetry acquisition and cloud transmission:
1. **Physical Loop:** A 12V DC pump circulates water from a closed reservoir through a 1/2" hydraulic pipe loop.
2. **Telemetry Sampling:** An ESP32 samples 5 physical sensing channels once per second.
3. **Aggregation:** Every 60 seconds, the ESP32 computes RMS (for vibration) and Mean (for current, temperature, pressure, flow).
4. **Cloud Transmission:** Sends a standard JSON payload over Wi-Fi via HTTPS POST to the Ingestion / Inference API.
5. **Controlled Fault Injection:** Allows manual fault induction (e.g., closing the ball valve to create hydraulic blockage/cavitation, or adding an eccentric weight to simulate unbalance) to trigger cloud alarms live during demonstration.

---

## 2. Corrected Bill of Materials (BOM) — 100% Practical & Verified

Everything listed below is available locally in Egypt (e.g., Bab El-Louk, Ram Electronics, Makers Electronics):

| # | Component | Exact Commercial Search Name | Qty | Approx Cost (EGP) | Technical Purpose |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | **Microcontroller** | **ESP32 NodeMCU Development Board** (38-pin, CP2102) | 1 | 280 to 350 | Central IoT controller with Wi-Fi & I2C/ADC |
| **2** | **Vibration Sensor (Motor)** | **ADXL345 3-Axis Accelerometer Module** | 1 | 90 to 120 | Measures motor casing vibration (I2C address `0x53`) |
| **3** | **Vibration Sensor (Coupling)** | **ADXL345 3-Axis Accelerometer Module** | 1 | 90 to 120 | Measures coupling vibration (I2C address `0x1D`, connect SDO to 3.3V) |
| **4** | **DC Current Sensor** | **ACS712 30A Current Sensor Module** | **1** | 70 to 110 | Measures 12V DC motor current draw (Do NOT buy SCT-013; SCT-013 is AC only!) |
| **5** | **Temperature Sensor** | **DS18B20 Waterproof Temperature Probe** | 1 | 80 to 110 | Measures motor/bearing housing surface temperature |
| **6** | **Discharge Pressure Sensor** | **G1/4" Pressure Transducer** (0 to 1.2 MPa, 0.5V–4.5V output) | 1 | 180 to 250 | Measures hydraulic head pressure in discharge line |
| **7** | **Water Flow Sensor** | **YF-S201 Turbine Flow Sensor** (1/2" G-thread) | 1 | 70 to 110 | Measures flow rate in L/min via pulse interrupts |
| **8** | **Precision ADC** | **ADS1115 16-Bit I2C ADC Module** | 1 | 90 to 130 | Reads analog voltage from Pressure & Current sensors cleanly |
| **9** | **Pump (12V DC)** | **12V DC High Pressure Diaphragm / Centrifugal Pump** (40W to 60W) | 1 | 380 to 550 | Test bench hydraulic pump |
| **10** | **Power Supply** | **12V 5A DC Switching Power Adapter** | 1 | 150 to 200 | Powers the 12V pump motor |
| **11** | **Step-down Regulator** | **LM2596 Buck Converter Module** | 1 | 45 to 70 | Steps 12V down to clean 5.0V for ESP32 and sensors |
| **12** | **Fault Injection Valve** | **1/2" Manual Ball Valve** (Brass or PVC) | 1 | 50 to 80 | Used to throttle flow and simulate hydraulic blockage |
| **13** | **Hydraulic Plumbing** | 1/2" flexible tubing (2m), 15L plastic bucket, hose clamps, G1/4 tee fitting | 1 set | 120 to 180 | Closed water recirculation circuit |
| **14** | **Passives & Wires** | 4.7kΩ resistor (pull-up for DS18B20), breadboard, jumper wire pack | 1 set | 50 to 80 | Electrical breadboard hookup |
| **TOTAL** | | | | **~1,650 to 2,350 EGP** | **Complete hardware budget** |

---

## 3. Physical Hardware Telemetry Channels

The physical prototype measures **5 independent physical phenomena** across 6 transducer channels:

| Transducer | Physical Mounting Location | Physical Quantity | Normal Bench Range |
| :--- | :--- | :--- | :--- |
| **ADXL345 #1 (`0x53`)** | Motor Body Exterior | Motor Radial Vibration RMS ($g$) | 0.1 to 0.8 g |
| **ADXL345 #2 (`0x1D`)** | Shaft Coupling Bracket | Coupling Vibration RMS ($g$) | 0.05 to 0.5 g |
| **ACS712 (30A)** | Pump Motor Positive Line | Motor DC Current (Amperes) | 1.8 to 3.5 A |
| **DS18B20** | Motor Casing Surface | Motor Body Temperature (°C) | 25 to 45 °C |
| **G1/4" Transducer** | Discharge Line Manifold | Discharge Pressure (bar) | 0.4 to 0.9 bar |
| **YF-S201 Flow** | Discharge Line Return | Volumetric Flow Rate (L/min) | 3.0 to 7.5 L/min |

> [!IMPORTANT]
> **Methodology Transfer vs. Weight Transfer:**  
> The machine learning model in the repository was trained on a large industrial two-stage municipal water pump dataset. The 12V DC benchtop test-rig has completely different physical units and nominal baseline ranges (e.g., 2 Amps vs. 15 Amps).  
> The prototype proves the **end-to-end integration pipeline** (sensor reading $\rightarrow$ ESP32 aggregation $\rightarrow$ cloud API $\rightarrow$ persistence engine $\rightarrow$ alert generation). In production, the prototype is baselined on its own clean operational data.

---

## 4. Electrical Wiring Blueprint

```
Power Rail Configuration:
  - 12V 5A Supply ===> 12V Pump Motor (Positive through power switch)
  - 12V 5A Supply ===> LM2596 Buck Converter IN+
  - LM2596 OUT+ (adjusted to exactly 5.0V) ===> ESP32 VIN, ACS712 VCC, Pressure Transducer VCC
  - Common Ground: ALL GND lines tied together in a single star point.

I2C Bus Connections (Shared SDA & SCL):
  - ESP32 GPIO 21 <---> SDA of ADS1115, ADXL345 (Motor), ADXL345 (Coupling)
  - ESP32 GPIO 22 <---> SCL of ADS1115, ADXL345 (Motor), ADXL345 (Coupling)
  - Power: 3.3V from ESP32 to VCC of ADS1115 and both ADXL345 boards.
  - Motor ADXL345 Address: SDO pin to GND  --> I2C Address 0x53
  - Coupling ADXL345 Address: SDO pin to 3.3V --> I2C Address 0x1D
  - ADS1115 Address: ADDR pin to GND --> I2C Address 0x48

Analog Signals (via ADS1115 16-Bit ADC):
  - ADS1115 Channel A0 <---> ACS712 Current Sensor OUT pin
  - ADS1115 Channel A1 <---> Pressure Sensor Signal pin (after 10k:10k voltage divider to protect 3.3V rail)

1-Wire Temperature (DS18B20):
  - Yellow Data wire <---> ESP32 GPIO 4
  - Add a 4.7 kΩ pull-up resistor between GPIO 4 and 3.3V rail.

Turbine Flow Sensor (YF-S201):
  - Yellow Pulse wire <---> ESP32 GPIO 34 (Interrupt capable pin)
```

---

## 5. Live Demonstration Fault Protocols

During project evaluation, the hardware team will demonstrate system reactivity using these safe tests:

### Test 1: Discharge Hydraulic Throttling (Blockage & Cavitation)
1. Let the pump run normally for 5 minutes with the ball valve 100% open.
2. Slowly close the manual ball valve to 75% closed.
3. **Observed Physical Effect:** Pressure gauge rises, flow meter drops sharply, motor current increases.
4. **Cloud Reaction:** Risk score climbs; persistence filter confirms sustained blockage; status escalates to WARNING.

### Test 2: Mechanical Imbalance
1. Attach a small magnetic weight (3 to 5 grams) to the coupling collar.
2. **Observed Physical Effect:** Vibration amplitude on both ADXL345 sensors jumps significantly.
3. **Cloud Reaction:** Status escalates to CRITICAL; primary anomalous telemetry correctly isolates the vibration channels.
