import pytest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """
    Smoke test to ensure all modules can be imported without syntax errors.
    """
    try:
        from src.calculators import fluids_calculator
        from src.calculators import psychrometrics_calculator
        from src.calculators import reaction_calculator
        from src.calculators import separation_calculator
        from src.calculators import thermo_calculator
        from src.utils import unit_manager
        from src.utils import ui_helper
    except ImportError as e:
        pytest.fail(f"Failed to import a module: {e}")
