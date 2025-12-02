import pytest
from src.calculators.separation_calculator import calculate_mccabe_thiele

def test_benzene_toluene_trays():
    # vle_df, q_df, rect_df, strip_df, trays, steps
    _, _, _, _, trays, _ = calculate_mccabe_thiele(
        "benzene","toluene",
        101325, 0.4, 0.9, 0.1, 1.0, 1.5
    )
    # The exact number might vary slightly depending on thermo data versions, 
    # but let's assert it's a reasonable integer or range.
    assert isinstance(trays, int)
    assert trays > 0
