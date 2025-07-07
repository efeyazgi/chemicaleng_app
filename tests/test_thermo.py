from thermo import Chemical

water = Chemical('water', T=300, P=101325)
print(f"Density: {water.rho} kg/m^3")
print(f"Viscosity: {water.mu} Pa.s")
print(f"Heat Capacity: {water.Cp} J/kg.K")
