import pytest
import json
from __future__ import annotations
import macsima_parser as mp


data = mp.load_json('../data/250128_macsima_output.json')

# --------------------------------------------------
# Experiment tests
# --------------------------------------------------

def test_get_experiment_name():
    """Test that the experiment name is extracted correctly."""
    extracted = mp.get_experiment_name(data['experiments'][0])
    expected = "250128_liver_OCT_FCRB 1"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_procedure_name():
    """Test that the procedure name is extracted correctly."""
    extracted = mp.get_procedure_name(data['experiments'][0])
    expected = "Standard procedure"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_racks():
    """Test that the racks are extracted correctly."""
    extracted = mp.get_racks(data['experiments'][0])
    expected = "250128_FCRB"
    # TODO: make sure this works with multiple racks
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_start_time():
    """Test that the start time is extracted correctly."""
    extracted = mp.get_start_time(data['experiments'][0])
    expected = "2025-01-28T15:53:36Z"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_end_time():
    """Test that the end time is extracted correctly."""
    extracted = mp.get_end_time(data['experiments'][0])
    expected = "2025-01-29T06:43:08Z"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_running_time():
    """Test that the running time is extracted correctly."""
    extracted = mp.get_running_time(data['experiments'][0])
    expected = "14h 49m 27s"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_used_disk_space():
    """Test that the used disk space is extracted correctly."""
    extracted = mp.get_used_disk_space(data['experiments'][0])
    expected = "178.364 KB"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"


# --------------------------------------------------
# ROI tests
# --------------------------------------------------

def test_get_roi_name():
    """Test that the ROI name is extracted correctly."""
    extracted = mp.get_roi_name(data['rois'][0])
    expected = "C Overview"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_roi_name(data['rois'][1])
    expected = "ROI 1"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_roi_shape_type():
    """Test that the ROI shape type is extracted correctly."""
    extracted = mp.get_roi_shape_type(data['rois'][0])
    expected = "Rectangle"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_roi_shape_type(data['rois'][1])
    expected = "Rectangle"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_roi_shape_height():
    """Test that the ROI shape height is extracted correctly."""
    extracted = mp.get_roi_shape_height(data['rois'][0])
    expected = "10"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_roi_shape_height(data['rois'][1])
    expected = "2.350855833425806"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_roi_shape_width():
    """Test that the ROI shape width is extracted correctly."""
    extracted = mp.get_roi_shape_width(data['rois'][0])
    expected = "19"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_roi_shape_width(data['rois'][1])
    expected = "2.6345827695784165"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_autofocus_method():
    """Test that the autofocus method is extracted correctly."""
    extracted = mp.get_autofocus_method(data['rois'][0])
    expected = "ImageBased"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_autofocus_method(data['rois'][1])
    expected = "ConstantZ"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

# --------------------------------------------------
# Sample tests
# --------------------------------------------------

def test_get_sample_name():
    """Test that the sample name is extracted correctly."""
    extracted = mp.get_sample_name(data['samples'][0])
    expected = "250128_liver_OCT_FCRB 1"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_sample_species():
    """Test that the sample species is extracted correctly."""
    extracted = mp.get_sample_species(data['samples'][0])
    expected = "Human"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_sample_type():
    """Test that the sample type is extracted correctly."""
    extracted = mp.get_sample_type(data['samples'][0])
    expected = "Tissue"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_sample_organ():
    """Test that the sample organ is extracted correctly."""
    extracted = mp.get_sample_type(data['samples'][0])
    expected = "Liver"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_sample_fixation_method():
    """Test that the sample fixation method is extracted correctly."""
    extracted = mp.get_sample_type(data['samples'][0])
    expected = "PFA"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

# --------------------------------------------------
# Procedure block tests
# --------------------------------------------------

def test_get_run_cycle_number():
    """Test that the run cycle number is extracted correctly."""
    extracted = mp.get_block_number(data['procedures'][0]['blocks'][5])
    expected = "1"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_number(data['procedures'][0]['blocks'][6])
    expected = "2"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_number(data['procedures'][0]['blocks'][7])
    expected = "3"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_block_type():
    """Test that the block type is extracted correctly."""
    extracted = mp.get_block_type(data['procedures'][0]['blocks'][0])
    expected = "Scan"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_type(data['procedures'][0]['blocks'][1])
    expected = "DefineROIs"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_type(data['procedures'][0]['blocks'][2])
    expected = "Scan"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_type(data['procedures'][0]['blocks'][3])
    expected = "Erase"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_type(data['procedures'][0]['blocks'][4])
    expected = "RestainNuclei"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_type(data['procedures'][0]['blocks'][5])
    expected = "RunCycle"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_block_name():
    """Test that the block name is extracted correctly."""
    extracted = mp.get_block_name(data['procedures'][0]['blocks'][0])
    expected = "Scan"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_name(data['procedures'][0]['blocks'][1])
    expected = "Define ROIs"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_name(data['procedures'][0]['blocks'][2])
    expected = "Scan"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_name(data['procedures'][0]['blocks'][3])
    expected = "Erase"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_name(data['procedures'][0]['blocks'][4])
    expected = "Restain Nuclei"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_name(data['procedures'][0]['blocks'][5])
    expected = "Run Cycle"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_block_magnification():
    """Test that the block magnification is extracted correctly."""
    extracted = mp.get_block_magnification(data['procedures'][0]['blocks'][0])
    expected = "Magnification_2x"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_magnification(data['procedures'][0]['blocks'][1])
    expected = "Magnification_20x"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_magnification(data['procedures'][0]['blocks'][2])
    expected = "N/A"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_magnification(data['procedures'][0]['blocks'][3])
    expected = "N/A"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_magnification(data['procedures'][0]['blocks'][4])
    expected = "N/A"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_magnification(data['procedures'][0]['blocks'][5])
    expected = "N/A"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_erase_bleaching_energy():
    """Test that the bleaching energy per channel for erase block is extracted correctly."""
    extracted = mp.get_block_magnification(data['procedures'][0]['blocks'][3])
    expected = [{"Channel": "FITC", "bleachingEnergy": 1980}, { "Channel": "PE", "bleachingEnergy": 840,}, {"Channel": "APC", "bleachingEnergy": 780,}]
    # TODO: make sure data types are defined
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_run_cycle_channel_info():
    """Test that the run cycle channel info is extracted correctly."""
    extracted = mp.get_run_cycle_channel_info(data['procedures'][0]['blocks'][5])
    expected = [
        {
            "Channel": "DAPI",
            "ChannelInfo": {}
        },
        {
            "Channel": "FITC",
            "ChannelInfo": {
                "Antigen": "TCR Vα7.2",
                "Clone": "REA179",
                "DilutionFactor" : 50,
                "IncubationTime": 30,
                "ReagentExposureTime": 56,
                "ExposureCoefficient": 330,
                "ActualExposureTime": 184.8,
                "ErasingMethod": "Bleaching",
                "BleachingEnergy": 400,
                "ValidatedFor": "PFA"
            },
        },
        {
            "Channel": "PE",
            "ChannelInfo": {
                "Antigen": "CD56",
                "Clone": "AF12-7H3",
                "DilutionFactor" : 50,
                "IncubationTime": 30,
                "ReagentExposureTime": 24,
                "ExposureCoefficient": 430,
                "ActualExposureTime": 103.2,
                "ErasingMethod": "Bleaching",
                "BleachingEnergy": 160,
                "ValidatedFor": "PFA"
            }   
    },
    {
        "Channel": "APC",
        "ChannelInfo": {
            "Antigen": "PYGL",
            "Clone": "N/A",
            "DilutionFactor" : 50,
            "IncubationTime": 30,
            "ReagentExposureTime": 240,
            "ExposureCoefficient": 100,
            "ActualExposureTime": 240,
            "ErasingMethod": "Bleaching",
            "BleachingEnergy": 470,
            "ValidatedFor": "PFA"
        }
    }
    ]
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

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

def test_add_numbers_to_run_cycles(blocks: dict[str, Any]) -> int:
    """Test for adding numbers to run cycles."""
    pass