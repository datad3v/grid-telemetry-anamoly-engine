# Grid Telemetry Anomaly Engine

An enterprise-ready diagnostic pipeline for SCADA solar grid edge Telemetry. Designed to detect solar inverter degradation, conversion efficiency drops, and operational anomalies across distributed renewable energy generation sites.

## Overview
- **Domain:** Utility & Renewable Energy (Smart Grid Telemetry)
- **Problem:** Solar inverters convert DC power to AC power for grid distribution. Inverter degradation or panel soiling leads to unaccounted generation losses during peak solar exposure hours.
- **Solution:** Ingests 15-minute interval SCADA generation logs joined with weather sensor data (irradiation, module temperature) to flag suboptimal conversion ratios (< 85%) and surface failing equipment IDs.

## Tech Stack
- Python 3.10+
- Pandas / NumPy (Data Transformation & Filtering)
- Plotly / Matplotlib (Telemetry Visualization)

## Setup & Running 
1. Clone the repository
2. Set up environment:
   ```bash
   ```bash 
   python3 -m venv .venv 
   source .venv/bin/activate
   pip install -r requirements.txt
3. Place Plant_1_Generation_Data.csv and Plant_1_Weather_Sensor_Data.csv in data/
4. Run the engine:
    python src/outpost_telemetry_engine.py
