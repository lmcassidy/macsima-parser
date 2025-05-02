import pytest
import json
from __future__ import annotations
import macsima_parser as mp


data = mp.load_json('../data/250128_macsima_output.json')

# --------------------------------------------------
# Experiment level tests
# --------------------------------------------------

def test_get_experiment_name():
    """Test that the experiment name is extracted correctly."""
    extracted = mp.get_experiment_name(data)
    expected = "250128_liver_OCT_FCRB 1"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_procedure_name():
    """Test that the procedure name is extracted correctly."""
    extracted = mp.get_procedure_name(data)
    expected = "Standard procedure"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"