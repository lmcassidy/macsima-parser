import json
import os
import types
from pathlib import Path

import pandas as pd
import pytest

# --------------------------------------------------
# Module under test
# --------------------------------------------------
import macsima_parser as mp


# --------------------------------------------------
# Helper fixtures & sample data
# --------------------------------------------------
@pytest.fixture
def sample_data():
    """Representative but lightweight JSON structure that exercises every
    branch we care about (experiment, procedures, reagents, …)."""
    return {
        "experiments": [
            {
                "name": "Exp‑1",
                "executionStartDateTime": "2025‑01‑01T10:00:00",
                "executionEndDateTime": "2025‑01‑01T12:00:00",
                "actualRunningTime": 7200,            # 2 h
                "usedDiskspace": 2 * 1024**3,         # 2 GiB
            }
        ],
        "racks": [{"name": "Rack‑A"}],
        "rois": [
            {
                "type": "Rectangle",
                "shape": {"x": 5, "y": 5, "width": 100, "height": 100},
                "autoFocus": {"method": "Laser"},
            }
        ],
        "samples": [
            {
                "name": "Sample‑1",
                "species": "Mouse",
                "sampleType": "Tissue",
                "organ": "Liver",
                "fixationMethod": "PFA",
            }
        ],
        "reagents": [
            {
                "bucketId": "b1",
                "antigenName": "CD3",
                "clone": "Clone‑1",
                "exposureTime": 100,
                "supportedFixationMethods": ["PFA"],
            },
            {
                "bucketId": "b2",
                "antigenName": "CD4",
                "clone": "Clone‑2",
                "exposureTime": 120,
                "supportedFixationMethods": ["PFA"],
            },
        ],
        "procedures": [
            {
                "comment": "Standard procedure",
                "blocks": [
                    {
                        "protocolBlockType": "protocolBlockType_Scan",
                        "comment": "Scan",
                        "magnification": 20,
                        "isEnabled": True,
                        "detectionSettings": [],
                    },
                    {
                        # This one must be suppressed by parse_blocks
                        "protocolBlockType": "protocolBlockType_RestainNuclei",
                        "comment": "Restain‑nuclei",
                    },
                    {
                        "protocolBlockType": "protocolBlockType_RunCycle",
                        "comment": "Run cycle 1",
                        "bucketIdMapping": {"DAPI": "b1", "FITC": "b2"},
                        "channels": [],            # not used by our parser
                        "erasingMethod": "Bleach",
                        "bleachingEnergy": 5,
                        "incubationTime": 15,
                        "dilutionFactor": 2,
                        "timeCoefficient": 120,   # 120 %
                    },
                ],
            }
        ],
    }


@pytest.fixture
def sample_json_file(tmp_path: Path, sample_data):
    """Write sample_data to a temporary file and return its path."""
    p = tmp_path / "sample.json"
    p.write_text(json.dumps(sample_data))
    return p


# --------------------------------------------------
# Pure‑function unit tests
# --------------------------------------------------
@pytest.mark.parametrize(
    "seconds, expected",
    [(0, (0, 0, 0)), (1, (0, 0, 1)), (61, (0, 1, 1)), (3661, (1, 1, 1))],
)
def test_convert_seconds_to_hms(seconds, expected):
    assert mp.convert_seconds_to_hms(seconds) == expected


@pytest.mark.parametrize(
    "bytes_, expected_gb",
    [(1024**3, 1.0), (2 * 1024**3, 2.0), (0, 0.0)],
)
def test_convert_bytes_to_gb(bytes_, expected_gb):
    assert mp.convert_bytes_to_gb(bytes_) == expected_gb


def test_load_json(sample_json_file):
    data = mp.load_json(sample_json_file)
    # Minimal sanity check
    assert data["experiments"][0]["name"] == "Exp‑1"


# --------------------------------------------------
# Parsing helpers
# --------------------------------------------------
def test_parse_experiment_level(sample_data):
    exp_dict, roi_list, samp_list = mp.parse_experiment_level(sample_data)

    assert exp_dict["Experiment Name"] == "Exp‑1"
    assert exp_dict["Running Time (h/m/s)"] == "2h 0m 0s"
    # 2 GiB exactly
    assert float(exp_dict["Used Disk Space (GB)"]) == pytest.approx(2.0)
    assert roi_list and samp_list                         # not empty
    assert roi_list[0]["Autofocus Method"] == "Laser"
    assert samp_list[0]["Organ"] == "Liver"


def test_parse_blocks(sample_data):
    blocks = mp.parse_blocks(sample_data)
    # Restain‑nuclei block should be skipped
    assert len(blocks) == 2
    types = {b["Block Type"] for b in blocks}
    assert "protocolBlockType_Scan" in types
    assert "protocolBlockType_RestainNuclei" not in types


def test_parse_run_cycles(sample_data):
    cycles = mp.parse_run_cycles(sample_data)
    # One cycle × 4 canonical channels
    assert len(cycles) == 4
    dapi_row = next(row for row in cycles if row["Channel"] == "DAPI")
    # 100 s base exposure × 1.20 coefficient
    assert dapi_row["Actual Exposure (s)"] == pytest.approx(120.0)
    # A channel not mapped to a reagent should say so
    apc_row = next(row for row in cycles if row["Channel"] == "APC")
    assert apc_row["Antigen"] == "Not in this cycle"


def test_parse_helpers_with_missing_data():
    """Empty / degenerate JSON should not break the helpers."""
    empty = {}
    exp_dict, roi_list, samp_list = mp.parse_experiment_level(empty)
    assert exp_dict == {}
    assert roi_list == []
    assert samp_list == []
    assert mp.parse_blocks(empty) == []
    assert mp.parse_run_cycles(empty) == []


# --------------------------------------------------
# end‑to‑end: main()
# --------------------------------------------------
def test_main_creates_excel(sample_json_file, tmp_path):
    output_file = tmp_path / "report.xlsx"
    mp.main(sample_json_file, output_file)
    assert output_file.exists()
