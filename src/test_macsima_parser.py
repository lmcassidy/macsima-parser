from __future__ import annotations
import pytest
import json
import macsima_parser as mp
from pathlib import Path
import logging
import pprint

# Basic configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()  # You can add FileHandler, SMTPHandler, etc.
    ]
)

logger = logging.getLogger(__name__)


# Create dummy data structure for testing
dummy_data = {
    "experiments": [
        {
            "name": "250128_liver_OCT_FCRB 1",
            "executionStartDateTime": "2025-01-28T15:53:36Z",
            "executionEndDateTime": "2025-01-29T06:43:08Z",
            "actualRunningTime": 53367,  # 14h 49m 27s
            "usedDiskspace": 182645,  # 178.364 KB
        }
    ],
    "procedures": [
        {
            "comment": "Standard procedure",
            "blocks": [
                {
                    "protocolBlockType": "protocolBlockType_Scan",
                    "comment": "Scan",
                    "magnification": "Magnification_2x",
                    "isEnabled": True,
                    "detectionSettings": [],
                },
                {
                    "protocolBlockType": "protocolBlockType_DefineROIs",
                    "comment": "Define ROIs",
                    "isEnabled": True,
                },
                {
                    "protocolBlockType": "protocolBlockType_Scan",
                    "comment": "Scan",
                    "magnification": "Magnification_20x",
                    "isEnabled": True,
                    "detectionSettings": [],
                },
                {
                    "protocolBlockType": "protocolBlockType_Erase",
                    "comment": "Erase",
                    "isEnabled": True,
                    "channels": [
                        {"channelName": "FITC", "bleachingEnergy": 1980},
                        {"channelName": "PE", "bleachingEnergy": 840},
                        {"channelName": "APC", "bleachingEnergy": 780}
                    ]
                },
                {
                    "protocolBlockType": "protocolBlockType_RestainNuclei",
                    "comment": "Restain Nuclei",
                    "isEnabled": True,
                },
                {
                    "protocolBlockType": "protocolBlockType_RunCycle",
                    "comment": "Run Cycle",
                    "isEnabled": True,
                    "bucketIdMapping": {"DAPI": "bucket1", "FITC": "bucket2", "PE": "bucket3", "APC": "bucket4", "Vio780": "bucket5"},
                    "channels": [],
                    "erasingMethod": "Bleach",
                    "bleachingEnergy": 5,
                    "incubationTime": 30,
                    "dilutionFactor": 50,
                    "timeCoefficient": 330,
                    "reagents": [
                        {
                            "channelName": "DAPI",
                            "bucketId": "bucket1",
                            "reagentExposureTime": 0,
                            "exposureCoefficient": 0,
                            "actualExposureTime": 0,
                            "erasingMethod": "",
                            "bleachingEnergy": 0
                        },
                        {
                            "channelName": "FITC",
                            "bucketId": "bucket2",
                            "reagentExposureTime": 56,
                            "exposureCoefficient": 330,
                            "actualExposureTime": 184.8,
                            "erasingMethod": "Bleaching",
                            "bleachingEnergy": 400
                        },
                        {
                            "channelName": "PE",
                            "bucketId": "bucket3",
                            "reagentExposureTime": 24,
                            "exposureCoefficient": 430,
                            "actualExposureTime": 103.2,
                            "erasingMethod": "Bleaching",
                            "bleachingEnergy": 160
                        },
                        {
                            "channelName": "APC",
                            "bucketId": "bucket4",
                            "reagentExposureTime": 240,
                            "exposureCoefficient": 100,
                            "actualExposureTime": 240.0,
                            "erasingMethod": "Bleaching",
                            "bleachingEnergy": 470
                        },
                        {
                            "channelName": "Vio780",
                            "bucketId": "bucket5",
                            "reagentExposureTime": 0,
                            "exposureCoefficient": 0,
                            "actualExposureTime": 0,
                            "erasingMethod": "",
                            "bleachingEnergy": 0
                        }
                    ]
                },
                {
                    "protocolBlockType": "protocolBlockType_RunCycle",
                    "comment": "Run Cycle",
                    "isEnabled": True,
                    "bucketIdMapping": {"DAPI": "bucket1", "FITC": "bucket2", "PE": "bucket3", "APC": "bucket4", "Vio780": "bucket5"},
                    "channels": [],
                    "erasingMethod": "Bleach",
                    "bleachingEnergy": 5,
                    "incubationTime": 30,
                    "dilutionFactor": 50,
                    "timeCoefficient": 330,
                    "reagents": []
                },
                {
                    "protocolBlockType": "protocolBlockType_RunCycle",
                    "comment": "Run Cycle",
                    "isEnabled": True,
                    "bucketIdMapping": {"DAPI": "bucket1", "FITC": "bucket2", "PE": "bucket3", "APC": "bucket4", "Vio780": "bucket5"},
                    "channels": [],
                    "erasingMethod": "Bleach",
                    "bleachingEnergy": 5,
                    "incubationTime": 30,
                    "dilutionFactor": 50,
                    "timeCoefficient": 330,
                    "reagents": []
                }
            ]
        }
    ],
    "racks": [
        {
            "name": "250128_FCRB"
        }
    ],
    "rois": [
        {
            "name": "C Overview",
            "type": "Rectangle",
            "shape": {
                "x": 0,
                "y": 0,
                "width": "19",
                "height": "10"
            },
            "autoFocus": {
                "method": "ImageBased"
            }
        },
        {
            "name": "ROI 1",
            "type": "Rectangle",
            "shape": {
                "x": 0,
                "y": 0,
                "width": "2.6345827695784165",
                "height": "2.350855833425806"
            },
            "autoFocus": {
                "method": "ConstantZ"
            }
        }
    ],
    "samples": [
        {
            "name": "250128_liver_OCT_FCRB",
            "species": "Human",
            "sampleType": "Tissue",
            "organ": "Liver",
            "fixationMethod": "PFA"
        }
    ],
    "reagents": [
        {
            "id": "bucket1",
            "bucketId": "bucket1",
            "antigenName": "",
            "clone": "",
            "exposureTime": 0,
            "supportedFixationMethods": ["PFA"],
            "antibody": "",
            "antibodyType": "",
            "hostSpecies": "",
            "isotype": "",
            "manufacturer": "",
            "name": "",
            "orderNumber": "",
            "species": ""
        },
        {
            "bucketId": "bucket2",
            "antigenName": "TCR Vα7.2",
            "clone": "REA179",
            "exposureTime": 56,
            "supportedFixationMethods": ["PFA"],
            "antibody": "TCR_Valpha7_2__REA179",
            "antibodyType": "REA",
            "hostSpecies": "human cell line",
            "isotype": "",
            "manufacturer": "MB",
            "name": "TCR Vα7.2 Antibody, anti-human, REAfinity™",
            "orderNumber": "130-123-685",
            "species": "human"
        },
        {
            "bucketId": "bucket3",
            "antigenName": "CD56",
            "clone": "AF12-7H3",
            "exposureTime": 24,
            "supportedFixationMethods": ["PFA"],
            "antibody": "CD56__AF12_7H3",
            "antibodyType": "Hybridoma",
            "hostSpecies": "mouse",
            "isotype": "",
            "manufacturer": "MB",
            "name": "CD56 Antibody, anti-human",
            "orderNumber": "130-113-307",
            "species": "human"
        },
        {
            "bucketId": "bucket4",
            "antigenName": "PYGL",
            "clone": "",
            "exposureTime": 240,
            "supportedFixationMethods": ["PFA"],
            "antibody": "PYGL",
            "antibodyType": "rabbit",
            "hostSpecies": "",
            "isotype": "",
            "manufacturer": "nordic biosite",
            "name": "PYGL",
            "orderNumber": "",
            "species": "Human"
        },
        {
            "bucketId": "bucket5",
            "antigenName": "",
            "clone": "",
            "exposureTime": 0,
            "supportedFixationMethods": ["PFA"],
            "antibody": "",
            "antibodyType": "",
            "hostSpecies": "",
            "isotype": "",
            "manufacturer": "",
            "name": "",
            "orderNumber": "",
            "species": ""
        }
    ]
}

data = dummy_data

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
    extracted = mp.get_procedure_name(data['procedures'][0])
    expected = "Standard procedure"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_rack_name():
    """Test that the rack name extracted correctly."""
    extracted = mp.get_rack_name(data['racks'][0])
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
    expected = "250128_liver_OCT_FCRB"
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
    extracted = mp.get_sample_organ(data['samples'][0])
    expected = "Liver"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_sample_fixation_method():
    """Test that the sample fixation method is extracted correctly."""
    extracted = mp.get_sample_fixation_method(data['samples'][0])
    expected = "PFA"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

# --------------------------------------------------
# Procedure block tests
# --------------------------------------------------

def test_get_run_cycle_number():
    """Test that the run cycle number is extracted correctly."""
    blocks = data['procedures'][0]['blocks']
    blocks_with_run_cycle_numbers = mp.add_numbers_to_run_cycles(blocks)
    extracted = mp.get_run_cycle_number(blocks_with_run_cycle_numbers[5])
    expected = 1
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_run_cycle_number(blocks_with_run_cycle_numbers[6])
    expected = 2
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_run_cycle_number(blocks_with_run_cycle_numbers[7])
    expected = 3
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
    expected = "N/A"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_magnification(data['procedures'][0]['blocks'][2])
    expected = "Magnification_20x"
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
    extracted = mp.get_erase_bleaching_energy(data['procedures'][0]['blocks'][3])
    expected = [{"Channel": "FITC", "bleachingEnergy": 1980}, { "Channel": "PE", "bleachingEnergy": 840,}, {"Channel": "APC", "bleachingEnergy": 780,}]
    # TODO: make sure data types are defined
    assert extracted == expected, f"Expected {expected}, but got {extracted}"

def test_get_run_cycle_channel_info():
    """Test that the run cycle channel info is extracted correctly."""
    bucket_lookup = mp.build_bucket_lookup(data)
    block         = data['procedures'][0]['blocks'][5]
    extracted = mp.get_run_cycle_channel_info(
        block,
        bucket_lookup=bucket_lookup,
    )
    pprint.pprint(data['procedures'][0]['blocks'][5]['reagents'])

    expected = [
        {
            "Channel": "DAPI",
            "ChannelInfo": {
                "Antigen": "",
                "Clone": "",
                "DilutionFactor": "",
                "IncubationTime": "",
                "ReagentExposureTime": "",
                "ExposureCoefficient": "",
                "ActualExposureTime": "",
                "ErasingMethod": "",
                "BleachingEnergy": "",
                "ValidatedFor": "",
                "Antibody": "",
                "AntibodyType": "",
                "HostSpecies": "",
                "Isotype": "",
                "Manufacturer": "",
                "Name": "",
                "OrderNumber": "",
                "Species": ""
            }
        },
        {
            "Channel": "FITC",
            "ChannelInfo": {
                "Antigen": "TCR Vα7.2",
                "Clone": "REA179",
                "DilutionFactor": 50,
                "IncubationTime": 30,
                "ReagentExposureTime": 56,
                "ExposureCoefficient": 330,
                "ActualExposureTime": 184.8,
                "ErasingMethod": "Bleaching",
                "BleachingEnergy": 400,
                "ValidatedFor": "PFA",
                "Antibody": "TCR_Valpha7_2__REA179",
                "AntibodyType": "REA",
                "HostSpecies": "human cell line",
                "Isotype": "",
                "Manufacturer": "MB",
                "Name": "TCR Vα7.2 Antibody, anti-human, REAfinity™",
                "OrderNumber": "130-123-685",
                "Species": "human"
            }
        },
        {
            "Channel": "PE",
            "ChannelInfo": {
                "Antigen": "CD56",
                "Clone": "AF12-7H3",
                "DilutionFactor": 50,
                "IncubationTime": 30,
                "ReagentExposureTime": 24,
                "ExposureCoefficient": 430,
                "ActualExposureTime": 103.2,
                "ErasingMethod": "Bleaching",
                "BleachingEnergy": 160,
                "ValidatedFor": "PFA",
                "Antibody": "CD56__AF12_7H3",
                "AntibodyType": "Hybridoma",
                "HostSpecies": "mouse",
                "Isotype": "",
                "Manufacturer": "MB",
                "Name": "CD56 Antibody, anti-human",
                "OrderNumber": "130-113-307",
                "Species": "human"
            }
        },
        {
            "Channel": "APC",
            "ChannelInfo": {
                "Antigen": "PYGL",
                "Clone": "",  # Make sure this matches your new code!
                "DilutionFactor": 50,
                "IncubationTime": 30,
                "ReagentExposureTime": 240,
                "ExposureCoefficient": 100,
                "ActualExposureTime": 240.0,
                "ErasingMethod": "Bleaching",
                "BleachingEnergy": 470,
                "ValidatedFor": "PFA",
                "Antibody": "PYGL",
                "AntibodyType": "rabbit",
                "HostSpecies": "",
                "Isotype": "",
                "Manufacturer": "nordic biosite",
                "Name": "PYGL",
                "OrderNumber": "",
                "Species": "Human"
            }
        },
        {
            "Channel": "Vio780",
            "ChannelInfo": {
                "Antigen": "",
                "Clone": "",
                "DilutionFactor": "",
                "IncubationTime": "",
                "ReagentExposureTime": "",
                "ExposureCoefficient": "",
                "ActualExposureTime": "",
                "ErasingMethod": "",
                "BleachingEnergy": "",
                "ValidatedFor": "",
                "Antibody": "",
                "AntibodyType": "",
                "HostSpecies": "",
                "Isotype": "",
                "Manufacturer": "",
                "Name": "",
                "OrderNumber": "",
                "Species": ""
            }
        }
    ]

    assert extracted == expected, f"Expected {expected}, but got {extracted}"


def test_reagent_details_extraction():
    # Suppose you have a RunCycle block with a reagent attached
    bucket_lookup = mp.build_bucket_lookup(data)
    block = data['procedures'][0]['blocks'][5]  # Adjust index as needed

    # Call the function that processes run cycle channel info
    extracted = mp.get_run_cycle_channel_info(block, bucket_lookup)

    # We expect the output to include extra reagent fields, even if some are blank
    for channel in extracted:
        info = channel.get("ChannelInfo", {})
        # These fields should always be present (blank if missing in data)
        for field in [
            "Antigen", "Clone", "DilutionFactor", "IncubationTime", "ReagentExposureTime", 
            "ExposureCoefficient", "ActualExposureTime", "ErasingMethod", "BleachingEnergy", "ValidatedFor",
            "Antibody", "AntibodyType", "HostSpecies", "Isotype", "Manufacturer", "Name", "OrderNumber", "Species"
        ]:
            assert field in info


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
                "Species": "Mouse",
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


def test_propagate_magnification():
    blocks = [
        {"blockType": "Scan", "magnification": "20x"},
        {"blockType": "DefineROIs"},
        {"blockType": "Scan"},
        {"blockType": "Erase", "magnification": "40x"},
        {"blockType": "RunCycle"}
    ]

    # Function you will write/fix!
    from macsima_parser import propagate_magnification

    updated = propagate_magnification(blocks)

    assert updated[0]["magnification"] == "20x"
    assert updated[1]["magnification"] == "20x"
    assert updated[2]["magnification"] == "20x"
    assert updated[3]["magnification"] == "40x"
    assert updated[4]["magnification"] == "40x"

# --------------------------------------------------
# Pure‑function unit tests
# --------------------------------------------------
@pytest.mark.parametrize(
    "seconds, expected",
    [(0, (0, 0, 0)), (1, (0, 0, 1)), (61, (0, 1, 1)), (3661, (1, 1, 1))],
)
def test_convert_seconds_to_hms(seconds, expected):
    assert mp.convert_seconds_to_hms(seconds) == expected


def test_load_json(sample_json_file):
    data = mp.load_json(sample_json_file)
    # Minimal sanity check
    assert data["experiments"][0]["name"] == "Exp‑1"

def test_add_numbers_to_run_cycles():
    """Test for adding numbers to run cycles."""
    blocks = data['procedures'][0]['blocks']
    blocks_with_run_cycle_numbers = mp.add_numbers_to_run_cycles(blocks)
    # assert that each block that is a run cycle has a runCycleNumber
    for block in blocks_with_run_cycle_numbers:
        if block.get("blockType") == "ProtocolBlockType_RunCycle":
            assert "runCycleNumber" in block
        else:
            assert "runCycleNumber" not in block