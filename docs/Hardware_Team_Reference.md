# Hardware Team Reference — End-Suction Centrifugal Irrigation Pump Test Bench

> **Target Asset:** Industrial End-Suction Centrifugal Irrigation Pump (Standard: Grundfos NB / Kirloskar DB Series)
> **Scale Implementation:** Benchtop Functional Prototype (ESP32-based Telemetry & Fault Injection Rig)
> **Version:** 2.0 — Standardized Machine Architecture
> **Audience:** Hardware & Embedded Systems Team

---

## 1. Target Machine Specification & Physical Context

Our AI model and predictive maintenance system are engineered specifically for:
- **Machine Type:** Horizontal End-Suction Centrifugal Irrigation Pump (Electric Motor-Driven).
- **Industrial Role:** Agricultural irrigation water lifting, booster station, and canal pumping.
- **Key Subsystems:**
  1. **Electric Drive Motor:** AC Induction Motor (casing, stator windings, drive-end / non-drive-end bearings).
  2. **Mechanical Flexible Coupling:** Connects the motor output shaft to the pump shaft.
  3. **Pump Housing & Volute:** Contains the impeller, shaft seal / stuffing box, and suction/discharge flanges.
  4. **Bearings Assembly:** Drive-end bearing supporting hydraulic radial/axial loads.

The hardware prototype built by the team acts as a **functional scale test-bench** mimicking the operational dynamics, electrical draw, temperature, and vibration signatures of this specific pump.

---

## 2. Sensor Placement on the Pump Assembly

Every physical sensor corresponds to an exact mechanical or electrical inspection point defined in pump maintenance standards (such as **ISO 10816-3** for vibration severity and **ANSI/HI 9.6**):

```
       [ELECTRIC MOTOR]               [COUPLING]              [PUMP VOLUTE]
   +-----------------------+              ||              +-------------------+
   |                       |              ||              |     Impeller      |
   | [sensor_05 / 11]      |         [sensor_13]          |                   |====> [sensor_48]
   | (Current CT Clamp)    |        (ADXL345 on           |                   |    Discharge Pressure
   |                       |       Coupling Guard)        |                   |
   | [sensor_00]           |                              | [sensor_28]       |
   | (ADXL345 Motor DE)    |                              | (Discharge Flow)  |
   |                       |                              +-------------------+
   | [sensor_40]           |                                        |
   | (DS18B20 Bearing Temp)|                                        | (Suction)
   +-----------------------+                                        v
```

### Sensor-to-Physical Asset Mapping:

| Sensor ID | Sensor Hardware Component | Exact Physical Mounting Location | Monitored Physical Phenomenon |
| :--- | :--- | :--- | :--- |
| **`sensor_00`** | ADXL345 Digital Accelerometer (Z/Radial) | Motor Drive-End (DE) Bearing Housing | Rotor unbalance, motor bearing inner/outer race defect, structural looseness. |
| **`sensor_04`** | Optical Tachometer / Hall Effect Sensor | Motor Output Shaft | Motor RPM, slip under load, cavitation-induced speed fluctuations. |
| **`sensor_05`** | ACS712-30A / SCT-013-030 Current Sensor | Motor Power Supply Line (Phase A) | Current draw, motor overloading, impeller clogging, dry running. |
| **`sensor_11`** | ACS712 / SCT-013 (or dual tap) | Motor Power Supply Line (Phase B) | Phase current imbalance, winding faults, electrical supply degradation. |
| **`sensor_13`** | ADXL345 Digital Accelerometer (X/Axial) | Coupling Housing / Bearing Pedestal | Shaft angular/parallel misalignment, worn flexible coupling spider. |
| **`sensor_28`** | YF-S201 Turbine Flow Sensor | Discharge Pipe | Flow discharge rate (L/min), loss of prime, impeller erosion/obstruction. |
| **`sensor_40`** | DS18B20 Waterproof Digital Probe | Motor DE Bearing External Casing | Bearing lubrication degradation, overheating due to excessive friction. |
| **`sensor_48`** | G1/4" Pressure Transducer (0–1.2 MPa) | Discharge Manifold (Volute Outlet) | Head pressure, pipe blockage, closed discharge valve, cavitation pressure drops. |

---

## 3. Bill of Materials (BOM) — Local Market (Egypt)

All components are readily available from local electronics vendors (e.g., Ram Electronics, Micro Center, Makers, Al-Mohandiseen) and plumbing suppliers:

| # | Item Description | Specification / Search Key | Qty | Estimated Cost (EGP) | Purpose / Notes |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | **Microcontroller Board** | ESP32 NodeMCU V1 (38-Pin, CP2102) | 1 | 280 – 350 | Central IoT Controller with Wi-Fi & Dual Core |
| **2** | **Vibration Accelerometer (Motor)** | ADXL345 Module (I2C/SPI Breakout) | 1 | 90 – 120 | Measures Motor Bearing Radial Vibration (`sensor_00`) |
| **3** | **Vibration Accelerometer (Coupling)** | ADXL345 Module (I2C/SPI Breakout) | 1 | 90 – 120 | Measures Coupling Misalignment Vibration (`sensor_13`) |
| **4** | **Motor Current Sensor** | ACS712 (30A DC) or SCT-013-030 (AC) | 1 | 70 – 130 | Senses motor current consumption (`sensor_05`) |
| **5** | **Bearing Temperature Probe** | DS18B20 Waterproof Stainless Probe | 1 | 80 – 110 | Real-time temperature of bearing housing (`sensor_40`) |
| **6** | **Discharge Pressure Transducer** | G1/4" 0–1.2 MPa (0.5V – 4.5V output) | 1 | 180 – 260 | Detects head pressure drops/surges (`sensor_48`) |
| **7** | **Precision I2C ADC** | ADS1115 16-Bit ADC Module | 1 | 90 – 130 | Reads Current & Pressure analog signals with zero noise |
| **8** | **Flow Meter (Impeller Proxy)** | YF-S201 Turbine Flow Sensor (1/2") | 1 | 70 – 110 | Monitors water flow / delivery rate (`sensor_28`) |
| **9** | **Centrifugal Pump Model** | 12V DC Diaphragm/Centrifugal Test Pump | 1 | 380 – 550 | 40W–60W water pump representing irrigation unit |
| **10** | **Power Supply** | 12V 5A DC Switching Power Adapter | 1 | 150 – 200 | Powers pump motor |
| **11** | **Step-down Regulator** | LM2596 DC-DC Buck Converter Module | 1 | 45 – 70 | Steps 12V down to clean 5V rail for ESP32 and sensors |
| **12** | **Passives & Hardware** | 4.7kΩ resistor, 10kΩ resistors, breadboard, wires | 1 set | 60 – 90 | Pull-ups for 1-Wire & voltage dividers |
| **13** | **Plumbing Hydraulic Loop** | 1/2" flexible tubing (2m), 10L bucket, fittings | 1 set | 100 – 150 | Closed loop for recirculating water |
| **14** | **Ball Valve (1/2")** | Manual Brass / PVC Ball Valve | 1 | 50 – 80 | Fault injection: flow throttling & head blockage |
| **TOTAL** | | | | **~1,700 – 2,400 EGP** | **Complete hardware budget** |

---

## 4. Hardware Wiring & Pinout Blueprint

```
ESP32 NodeMCU Pinout Configuration
==================================

[I2C Bus: Shared by ADS1115, ADXL345 #1, ADXL345 #2]
  - ESP32 GPIO 21  <--->  SDA of ADS1115, ADXL345 (DE), ADXL345 (Coupling)
  - ESP32 GPIO 22  <--->  SCL of ADS1115, ADXL345 (DE), ADXL345 (Coupling)
  - ESP32 3.3V     <--->  VCC of ADS1115, both ADXL345 boards
  - ESP32 GND      <--->  Common GND (All modules + Power supply)

[I2C Addressing Configuration]
  - ADXL345 (Motor Bearing `sensor_00`): SDO connected to GND  --> I2C Address 0x53
  - ADXL345 (Coupling `sensor_13`):      SDO connected to 3.3V --> I2C Address 0x1D
  - ADS1115 (16-bit ADC):                ADDR connected to GND --> I2C Address 0x48

[1-Wire Temperature: DS18B20 `sensor_40`]
  - Red (VCC)      <--->  ESP32 3.3V
  - Black (GND)    <--->  ESP32 GND
  - Yellow (DATA)  <--->  ESP32 GPIO 4
  - Pull-up Resistor: 4.7 kΩ between GPIO 4 and 3.3V

[Pulse Flow Meter: YF-S201 `sensor_28`]
  - Red (VCC)      <--->  5V (from Buck Converter)
  - Black (GND)    <--->  ESP32 GND
  - Yellow (PULSE) <--->  ESP32 GPIO 34 (Interrupt-capable pin)

[Analog Subsystem via ADS1115]
  - ADS1115 A0 Channel <---> ACS712 OUT (Current Sensor)
  - ADS1115 A1 Channel <---> Pressure Sensor Signal (through 10k:10k voltage divider)

[Power Distribution Rail]
  - 12V 5A Supply ---> Pump Motor Positive (via switch/relay) & LM2596 IN+
  - LM2596 OUT+ (adjusted to 5.0V) ---> ESP32 VIN, ACS712 VCC, Pressure Transducer VCC
  - All Grounds tied together (Star Ground topology to prevent ground loops).
```

---

## 5. ESP32 Real-Time Firmware Architecture

The ESP32 runs a deterministic sampling loop:
1. **High-Frequency Sampling (1 Hz):** Samples acceleration RMS, instantaneous current, pressure, and temperature.
2. **Deterministic Minute Aggregation (60-sec window):**
   - Calculates **RMS** for acceleration (true vibration severity conforming to ISO 10816).
   - Calculates **Mean** for Current, Pressure, Temperature, and Flow.
3. **NTP Timestamping:** Generates standard ISO-8601 UTC timestamp (`YYYY-MM-DDTHH:MM:SSZ`).
4. **Cloud Transmission:** Transmits payload via HTTP POST to the AI Ingestion Service.
5. **Local SPIFFS Resilient Storage:** If Wi-Fi disconnects, records are written locally to SPIFFS flash and burst-streamed sequentially upon reconnect.

```json
{
  "pump_id": "PUMP_IRRIGATION_001",
  "timestamp": "2024-03-15T10:30:00Z",
  "sensor_00": 1.45,
  "sensor_04": 2940.0,
  "sensor_05": 14.8,
  "sensor_11": 14.7,
  "sensor_13": 2.15,
  "sensor_28": 185.2,
  "sensor_40": 48.6,
  "sensor_48": 4.2
}
```

---

## 6. Fault Simulation Protocols (Validating AI Detection)

To prove to the examination committee that our predictive maintenance system detects developing faults ahead of time, the hardware team will execute these controlled scenarios:

### Scenario 1: Hydraulic Blockage & Cavitation (Discharge Throttling)
- **Procedure:** Turn the manual ball valve on the discharge line to 75% closed.
- **Expected Physical Response:** Discharge pressure spikes, flow rate (`sensor_28`) drops, motor current (`sensor_05`) rises due to increased hydraulic resistance.
- **AI Alert:** The model flags a WARNING within 10–20 mins, attributing the anomaly to `sensor_05` / `sensor_48`.

### Scenario 2: Mechanical Unbalance & Bearing Degradation
- **Procedure:** Mount a small eccentric mass (5g magnetic counterweight) on the coupling collar or slightly loosen one motor foundation bolt.
- **Expected Physical Response:** Vibration spikes drastically on `sensor_00` and `sensor_13`.
- **AI Alert:** Health Index drops below 50% (CRITICAL); RAG recommends bearing/alignment inspection.

### Scenario 3: Thermal Stress (Simulated Bearing Lubrication Starvation)
- **Procedure:** Apply gentle localized warm air to the bearing probe housing using a variable heat element.
- **Expected Physical Response:** `sensor_40` demonstrates an abnormal positive delta compared to the 60-min baseline.
- **AI Alert:** Early warning triggered based on thermal gradient anomaly.
