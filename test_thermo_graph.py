
import pandas as pd
from src.calculators.thermo_calculator import generate_plot_data

def test_graph_generation():
    print("Testing graph generation...")
    
    # Test Case 1: SI Units, Water
    chemical_name = "water"
    pressure = 101325.0 # Pa
    unit_system = "SI"
    prop_key = "rho" # Density
    temp_min = 300.0 # K
    temp_max = 350.0 # K
    
    print(f"\nCase 1: {chemical_name}, {unit_system}, {prop_key}, {temp_min}-{temp_max} K")
    df = generate_plot_data(chemical_name, pressure, unit_system, prop_key, temp_min, temp_max)
    print("Result DataFrame:")
    print(df)
    if df.empty:
        print("ERROR: DataFrame is empty!")
    
    # Test Case 2: Metric Units, Ethanol
    chemical_name = "ethanol"
    pressure = 1.0 # bar
    unit_system = "Metric (CGS)"
    prop_key = "mu" # Viscosity
    temp_min = 20.0 # C
    temp_max = 60.0 # C
    
    print(f"\nCase 2: {chemical_name}, {unit_system}, {prop_key}, {temp_min}-{temp_max} C")
    df = generate_plot_data(chemical_name, pressure, unit_system, prop_key, temp_min, temp_max)
    print("Result DataFrame:")
    print(df)
    if df.empty:
        print("ERROR: DataFrame is empty!")

    # Test Case 3: Manual Units
    chemical_name = "toluene"
    pressure = 1.0 # atm
    unit_system = "Manual"
    prop_key = "Cp"
    temp_min = 25.0 # C
    temp_max = 100.0 # C
    manual_units = {'P': 'atm', 'T': 'degC', 'Cp': 'J/(kg*K)'} # Example manual units
    
    print(f"\nCase 3: {chemical_name}, {unit_system}, {prop_key}, {temp_min}-{temp_max} C (Manual)")
    df = generate_plot_data(chemical_name, pressure, unit_system, prop_key, temp_min, temp_max, manual_units)
    print("Result DataFrame:")
    print(df)
    if df.empty:
        print("ERROR: DataFrame is empty!")

if __name__ == "__main__":
    test_graph_generation()
