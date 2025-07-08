import pytest
from src.calculators.separation_calculator import calculate_theoretical_trays

def test_benzene_toluene_trays():
    trays, pts = calculate_theoretical_trays(
        "benzene","toluene",
        101325, 0.4, 0.9, 0.1, 1.0, 1.5
    )
    assert trays == 12
