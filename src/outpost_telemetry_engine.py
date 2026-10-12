import pandas as pd
import numpy as np
from pathlib import Path

def run_telemetry_audit(data_dir: str = "data"):
    """
    Ingests 15-minute SCADA telemetry and weather sensor logs to flag suboptimal solar inverter performance during active irradiance windows.
    """
    data_path = Path(data_dir)
    gen_file = data_path / "Plant_1_Generation_Data.csv"
    weather_file = data_path / "Plant_1_Weather_Sensor_Data.csv"

    if not gen_file.exists() or not weather_file.exists():
        raise FileNotFoundError(
            f"Missing required CSV files in '{data_dir}' directory. Please ensure both 'Plant_1_Generation_Data.csv' " 
            f"and 'Plant_1_Weather_Sensor_Data.csv' are present."
        )

    print("--> Ingesting raw SCADA edge logs...")
    # Read telemetry & weather CSVs into pandas DataFrames
    gen_df = pd.read_csv(gen_file)
    weather_df = pd.read_csv(weather_file)

    # Standardize timestamps
    gen_df['DATE_TIME'] = pd.to_datetime(gen_df['DATE_TIME'], format='mixed')
    weather_df['DATE_TIME'] = pd.to_datetime(weather_df['DATE_TIME'], format='mixed')

    print("--> Executing telemetry-weather join...")
    # Join generation records with weather sensor metrics on DATE_TIME 
    merged_df = pd.merge(
        gen_df,
        weather_df[['DATE_TIME', 'AMBIENT_TEMPERATURE', 'MODULE_TEMPERATURE', 'IRRADIATION']],
        on='DATE_TIME',
        how='inner'
    )

    print("--> Computing inverter conversion efficiency (DC -> AC)...")
    # Compute DC to AC ratio: avoid zero-division when inactive at night
    merged_df['CONVERSION_EFFICIENCY'] = np.where(
        merged_df['DC_POWER'] > 0,
        (merged_df['AC_POWER'] / merged_df['DC_POWER']) * 100,
        np.nan
    )

    print("--> Evaluating anomaly rules against active solar windows...")
    # Define Anomaly Rule: Active sunlight (Irradiation > 0.2) but conversion drops below 85% or AC yields 0
    anomalies = merged_df[
        (merged_df['IRRADIATION'] > 0.2) &
        ((merged_df['CONVERSION_EFFICIENCY'] < 85.0) | (merged_df['AC_POWER'] == 0))
    ]

    # Aggregate metrics by Inverter (SOURCE_KEY)
    fault_summary = anomalies.groupby('SOURCE_KEY').agg(
        fault_event_count=('DATE_TIME', 'count'),
        avg_efficiency_pct=('CONVERSION_EFFICIENCY', 'mean'),
        max_irradiation=('IRRADIATION', 'max'),
        avg_module_temp=('MODULE_TEMPERATURE', 'mean')
    ).reset_index().sort_values(by='fault_event_count', ascending=False)

    print("\n" + "="*60)
    print("         OUTPOST-07 GRID DIAGNOSTIC EXECUTIVE REPORT         ")
    print("="*60)
    print(f"Total Telemetry Records Processed: {len(merged_df):,}")
    print(f"Total Anomalous Readings Detected: {len(anomalies):,}")
    print(f"Unique Inverters Flagged for Degradation: {len(fault_summary)}")
    print("\nTop 5 Priority Inverters Requiring Field Maintenance:")
    print("-" * 60)

    # Display top failing hardware IDs
    for idx, row in fault_summary.head(5).iterrows():
        print(
            f"Hardware ID : {row['SOURCE_KEY']}\n"
            f"  Fault Count  : {row['fault_event_count']} events\n"
            f"  Avg Eff.     : {row['avg_efficiency_pct']:.2f}%\n"
            f"  Module Temp. : {row['avg_module_temp']:.2f} °C\n"
        )
    print("="*60)

    # Save summary report locally
    output_path = data_path / "inverter_fault_summary.csv"
    fault_summary.to_csv(output_path, index=False)
    print(f"--> Diagnostic audit exported to: {output_path}\n")

if __name__ == "__main__":
    run_telemetry_audit()