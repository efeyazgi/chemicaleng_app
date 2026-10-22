from thermo import Chemical


def test_liquid_water_properties_at_300_kelvin():
    water = Chemical('water', T=300, P=101325)
    # Broad physical bounds avoid coupling this smoke test to a data version.
    assert water.phase == 'l'
    assert 990 < water.rho < 1000  # kg/m^3
    assert 0.0008 < water.mu < 0.0010  # Pa.s
    assert 4100 < water.Cp < 4300  # J/(kg.K)
