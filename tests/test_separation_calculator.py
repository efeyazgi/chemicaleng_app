import numpy as np
import pytest

from src.calculators.separation_calculator import (
    calculate_mccabe_thiele_lines,
    calculate_theoretical_trays,
    generate_vle_data,
)


def test_benzene_toluene_vle_at_atmospheric_pressure():
    vle = generate_vle_data('benzene', 'toluene', 101325, n_points=51)
    assert list(vle.columns) == ['x', 'y']
    assert np.isfinite(vle.to_numpy()).all()
    assert vle.iloc[0].tolist() == [0.0, 0.0]
    assert vle.iloc[-1].tolist() == [1.0, 1.0]
    assert vle['y'].between(0, 1).all()
    assert (np.diff(vle['y']) > 0).all()
    assert (vle['y'].iloc[1:-1] > vle['x'].iloc[1:-1]).all()
    # Reference range for the ideal atmospheric benzene/toluene x-y curve.
    assert 0.70 < vle.iloc[25]['y'] < 0.73


@pytest.mark.parametrize('q', [0.0, 0.5, 1.0])
def test_operating_lines_join_and_satisfy_feed_balance(q):
    zf, xd, xb, reflux = 0.5, 0.95, 0.05, 3.0
    _, q_line, rect, strip = calculate_mccabe_thiele_lines(
        'benzene', 'toluene', 101325, zf, xd, xb, q, reflux
    )
    assert rect.iloc[0].to_numpy() == pytest.approx(strip.iloc[-1].to_numpy())
    assert rect.iloc[-1].to_numpy() == pytest.approx([xd, xd])
    assert strip.iloc[0].to_numpy() == pytest.approx([xb, xb])
    x, y = rect.iloc[0]
    # Feed balance in implicit form also covers the vertical q=1 case.
    assert q * x - (q - 1) * y == pytest.approx(zf)
    assert y == pytest.approx((reflux * x + xd) / (reflux + 1))
    assert np.isfinite(q_line.to_numpy()).all()


@pytest.mark.parametrize('q', [0.0, 1.0])
def test_tray_stepping_reaches_bottoms_with_fewer_stages_at_higher_reflux(q):
    counts = []
    for reflux in (3.0, 5.0):
        trays, points = calculate_theoretical_trays(
            'benzene', 'toluene', 101325, 0.5, 0.95, 0.05, q, reflux
        )
        assert isinstance(trays, int)
        assert 1 < trays < 50
        assert np.isfinite(points).all()
        assert points[0] == (0.95, 0.95)
        assert points[-1][0] <= 0.05
        assert (np.diff(np.asarray(points)[:, 0]) <= 1e-10).all()
        counts.append(trays)
    assert counts[1] < counts[0]


def test_unknown_component_is_rejected():
    with pytest.raises(ValueError, match='Antoine coefficients'):
        generate_vle_data('unknown', 'toluene', 101325)
