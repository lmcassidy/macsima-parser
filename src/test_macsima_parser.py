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
                    "blockType": "ProtocolBlockType_Scan",
                    "name": "Scan",
                    "comment": "Scan",
                    "magnification": "Magnification_2x",
                    "isEnabled": True,
                    "detectionSettings": [],
                },
                {
                    "blockType": "ProtocolBlockType_DefineROIs",
                    "name": "Define ROIs",
                    "comment": "Define ROIs",
                    "isEnabled": True,
                },
                {
                    "blockType": "ProtocolBlockType_Scan",
                    "name": "Scan",
                    "comment": "Scan",
                    "magnification": "Magnification_20x",
                    "isEnabled": True,
                    "detectionSettings": [],
                },
                {
                    "blockType": "ProtocolBlockType_Erase",
                    "name": "Erase",
                    "comment": "Erase",
                    "isEnabled": True,
                    "photos": {
                        "FITC": {"fluorochromeType": "FluorochromeType_FITC", "bleachingEnergy": 1980, "isEnabled": True},
                        "PE": {"fluorochromeType": "FluorochromeType_PE", "bleachingEnergy": 840, "isEnabled": True},
                        "APC": {"fluorochromeType": "FluorochromeType_APC", "bleachingEnergy": 780, "isEnabled": True}
                    }
                },
                {
                    "blockType": "ProtocolBlockType_RestainNuclei",
                    "name": "Restain Nuclei",
                    "comment": "Restain Nuclei",
                    "isEnabled": True,
                },
                {
                    "blockType": "ProtocolBlockType_RunCycle",
                    "name": "Run Cycle",
                    "comment": "Run Cycle",
                    "isEnabled": True,
                    "bucketIdMapping": {"DAPI": "bucket1", "FITC": "bucket2", "PE": "bucket3", "APC": "bucket4", "Vio780": "bucket5"},
                    "channels": [],
                    "erasingMethod": "Bleach",
                    "bleachingEnergy": 5,
                    "incubationTime": 30,
                    "dilutionFactor": 50,
                    "timeCoefficient": 330,
                    "reagents": {
                        "DetectionChannel_1": {
                            "bucketId": "bucket1",
                            "dilutionFactor": 50,
                            "incubationTime": 30,
                            "exposureTimeAndCoefficient": {"timeCoefficient": 0},
                            "erasingMethod": "",
                            "bleachingEnergy": 0,
                            "bleachingTime": 0
                        },
                        "DetectionChannel_2": {
                            "bucketId": "bucket2",
                            "dilutionFactor": 50,
                            "incubationTime": 30,
                            "exposureTimeAndCoefficient": {"timeCoefficient": 330},
                            "erasingMethod": "ErasingMethod_Bleaching",
                            "bleachingEnergy": 400,
                            "bleachingTime": 15
                        },
                        "DetectionChannel_3": {
                            "bucketId": "bucket3",
                            "dilutionFactor": 50,
                            "incubationTime": 30,
                            "exposureTimeAndCoefficient": {"timeCoefficient": 430},
                            "erasingMethod": "ErasingMethod_Bleaching",
                            "bleachingEnergy": 160,
                            "bleachingTime": 20
                        },
                        "DetectionChannel_4": {
                            "bucketId": "bucket4",
                            "dilutionFactor": 50,
                            "incubationTime": 30,
                            "exposureTimeAndCoefficient": {"timeCoefficient": 100},
                            "erasingMethod": "ErasingMethod_Bleaching",
                            "bleachingEnergy": 470,
                            "bleachingTime": 25
                        },
                        "DetectionChannel_5": {
                            "bucketId": "bucket5",
                            "dilutionFactor": 50,
                            "incubationTime": 30,
                            "exposureTimeAndCoefficient": {"timeCoefficient": 0},
                            "erasingMethod": "",
                            "bleachingEnergy": 0,
                            "bleachingTime": 0
                        }
                    }
                },
                {
                    "blockType": "ProtocolBlockType_RunCycle",
                    "name": "Run Cycle",
                    "comment": "Run Cycle",
                    "isEnabled": True,
                    "bucketIdMapping": {"DAPI": "bucket1", "FITC": "bucket2", "PE": "bucket3", "APC": "bucket4", "Vio780": "bucket5"},
                    "channels": [],
                    "erasingMethod": "Bleach",
                    "bleachingEnergy": 5,
                    "incubationTime": 30,
                    "dilutionFactor": 50,
                    "timeCoefficient": 330,
                    "reagents": {}
                },
                {
                    "blockType": "ProtocolBlockType_RunCycle",
                    "name": "Run Cycle",
                    "comment": "Run Cycle",
                    "isEnabled": True,
                    "bucketIdMapping": {"DAPI": "bucket1", "FITC": "bucket2", "PE": "bucket3", "APC": "bucket4", "Vio780": "bucket5"},
                    "channels": [],
                    "erasingMethod": "Bleach",
                    "bleachingEnergy": 5,
                    "incubationTime": 30,
                    "dilutionFactor": 50,
                    "timeCoefficient": 330,
                    "reagents": {}
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
                "Type": "ShapeType_Rectangle",
                "Data": "{\"Width\": 19, \"Height\": 10}"
            },
            "autoFocus": {
                "method": "ImageBased"
            }
        },
        {
            "name": "ROI 1",
            "type": "Rectangle",
            "shape": {
                "Type": "ShapeType_Rectangle",
                "Data": "{\"Width\": 2.6345827695784165, \"Height\": 2.350855833425806}"
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
            "id": "bucket2",
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
            "id": "bucket3",
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
            "id": "bucket4",
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
            "id": "bucket5",
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
    expected = "182.645 KB"
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
    expected = "2x"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_magnification(data['procedures'][0]['blocks'][1])
    expected = "N/A"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    extracted = mp.get_block_magnification(data['procedures'][0]['blocks'][2])
    expected = "20x"
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


def test_get_block_magnification_with_none():
    """Test that the block magnification handles None values correctly."""
    # Test case where magnification key exists but value is None
    block_with_none_magnification = {
        "blockType": "ProtocolBlockType_Scan",
        "name": "Test Block",
        "magnification": None
    }
    
    # This should not raise an AttributeError
    extracted = mp.get_block_magnification(block_with_none_magnification)
    expected = "N/A"
    assert extracted == expected, f"Expected {expected}, but got {extracted}"
    
    # Test case where magnification key doesn't exist
    block_without_magnification = {
        "blockType": "ProtocolBlockType_Scan",
        "name": "Test Block"
    }
    
    extracted = mp.get_block_magnification(block_without_magnification)
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
                "DilutionFactor": 50,
                "IncubationTime": 30,
                "ReagentExposureTime": "",
                "ExposureCoefficient": 0,
                "ActualExposureTime": "",
                "ErasingMethod": "",
                "BleachingEnergy": 0,
                "BleachingTime": 0,
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
                "Antigen": "",
                "Clone": "",
                "DilutionFactor": 50,
                "IncubationTime": 30,
                "ReagentExposureTime": "",
                "ExposureCoefficient": 330,
                "ActualExposureTime": "",
                "ErasingMethod": "Bleaching",
                "BleachingEnergy": 400,
                "BleachingTime": 15,
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
            "Channel": "PE",
            "ChannelInfo": {
                "Antigen": "",
                "Clone": "",
                "DilutionFactor": 50,
                "IncubationTime": 30,
                "ReagentExposureTime": "",
                "ExposureCoefficient": 430,
                "ActualExposureTime": "",
                "ErasingMethod": "Bleaching",
                "BleachingEnergy": 160,
                "BleachingTime": 20,
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
            "Channel": "APC",
            "ChannelInfo": {
                "Antigen": "",
                "Clone": "",
                "DilutionFactor": 50,
                "IncubationTime": 30,
                "ReagentExposureTime": "",
                "ExposureCoefficient": 100,
                "ActualExposureTime": "",
                "ErasingMethod": "Bleaching",
                "BleachingEnergy": 470,
                "BleachingTime": 25,
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
            "Channel": "Vio780",
            "ChannelInfo": {
                "Antigen": "",
                "Clone": "",
                "DilutionFactor": 50,
                "IncubationTime": 30,
                "ReagentExposureTime": "",
                "ExposureCoefficient": 0,
                "ActualExposureTime": "",
                "ErasingMethod": "",
                "BleachingEnergy": 0,
                "BleachingTime": 0,
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
            "ExposureCoefficient", "ActualExposureTime", "ErasingMethod", "BleachingEnergy", "BleachingTime", "ValidatedFor",
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


def test_format_column_header():
    """Test that column headers are formatted with line breaks."""
    # Test basic camelCase
    assert mp.format_column_header("BleachingEnergy") == "Bleaching\nEnergy"
    assert mp.format_column_header("DilutionFactor") == "Dilution\nFactor"
    
    # Test multi-word camelCase
    assert mp.format_column_header("ActualExposureTime") == "Actual\nExposure\nTime"
    assert mp.format_column_header("UsedDiskSpace") == "Used\nDisk\nSpace"
    
    # Test acronym patterns
    assert mp.format_column_header("ROIName") == "ROI\nName"
    assert mp.format_column_header("XMLData") == "XML\nData"
    
    # Test single words (no change)
    assert mp.format_column_header("Species") == "Species"
    assert mp.format_column_header("Height") == "Height"
    
    # Test empty string
    assert mp.format_column_header("") == ""
    
    # Test already formatted strings
    assert mp.format_column_header("Already\nFormatted") == "Already\nFormatted"


def test_format_dict_headers():
    """Test that dictionary keys are formatted with line breaks."""
    input_dict = {
        "BleachingEnergy": 100,
        "DilutionFactor": 50,
        "Species": "Human",
        "ROIName": "Test ROI"
    }
    
    expected = {
        "Bleaching\nEnergy": 100,
        "Dilution\nFactor": 50,
        "Species": "Human",
        "ROI\nName": "Test ROI"
    }
    
    result = mp.format_dict_headers(input_dict)
    assert result == expected
    
    # Test empty dictionary
    assert mp.format_dict_headers({}) == {}
    
    # Test dictionary with single key
    single_key_dict = {"TestKey": "value"}
    expected_single = {"Test\nKey": "value"}
    assert mp.format_dict_headers(single_key_dict) == expected_single


def test_add_blank_lines_between_run_cycles():
    """Test that blank lines are added between different run cycles."""
    # Test with multiple run cycles
    input_rows = [
        {"Block\nType": "Scan", "Run\nCycle\nNumber": "", "Channel": "DAPI"},
        {"Block\nType": "RunCycle", "Run\nCycle\nNumber": "1", "Channel": "DAPI"},
        {"Block\nType": "RunCycle", "Run\nCycle\nNumber": "1", "Channel": "FITC"},
        {"Block\nType": "RunCycle", "Run\nCycle\nNumber": "2", "Channel": "DAPI"},
        {"Block\nType": "RunCycle", "Run\nCycle\nNumber": "2", "Channel": "FITC"},
        {"Block\nType": "RunCycle", "Run\nCycle\nNumber": "3", "Channel": "DAPI"},
    ]
    
    result = mp.add_blank_lines_between_run_cycles(input_rows)
    
    # Should have 8 rows total (6 original + 2 blank lines)
    assert len(result) == 8
    
    # Check that blank lines are inserted at the right positions
    assert result[0] == input_rows[0]  # Scan block
    assert result[1] == input_rows[1]  # RunCycle 1, DAPI
    assert result[2] == input_rows[2]  # RunCycle 1, FITC
    
    # Blank line after run cycle 1
    assert result[3] == {"Block\nType": "", "Run\nCycle\nNumber": "", "Channel": ""}
    
    assert result[4] == input_rows[3]  # RunCycle 2, DAPI
    assert result[5] == input_rows[4]  # RunCycle 2, FITC
    
    # Blank line after run cycle 2
    assert result[6] == {"Block\nType": "", "Run\nCycle\nNumber": "", "Channel": ""}
    
    assert result[7] == input_rows[5]  # RunCycle 3, DAPI
    
    # Test empty list
    assert mp.add_blank_lines_between_run_cycles([]) == []
    
    # Test single run cycle (no blank lines should be added)
    single_cycle = [
        {"Block\nType": "RunCycle", "Run\nCycle\nNumber": "1", "Channel": "DAPI"},
        {"Block\nType": "RunCycle", "Run\nCycle\nNumber": "1", "Channel": "FITC"},
    ]
    result_single = mp.add_blank_lines_between_run_cycles(single_cycle)
    assert result_single == single_cycle  # No changes
    
    # Test non-RunCycle blocks only
    non_run_cycle = [
        {"Block\nType": "Scan", "Run\nCycle\nNumber": "", "Channel": "DAPI"},
        {"Block\nType": "Erase", "Run\nCycle\nNumber": "", "Channel": "FITC"},
    ]
    result_non_run = mp.add_blank_lines_between_run_cycles(non_run_cycle)
    assert result_non_run == non_run_cycle  # No changes


def test_get_erase_channel_info():
    """Test that erase channel info is extracted correctly."""
    # Test with erase block from dummy data
    erase_block = data['procedures'][0]['blocks'][3]  # This should be an erase block
    
    extracted = mp.get_erase_channel_info(erase_block)
    
    # Should return a list of channel info dictionaries
    assert isinstance(extracted, list)
    assert len(extracted) == 3  # FITC, PE, APC
    
    # Check first channel
    assert extracted[0]["Channel"] == "FITC"
    assert extracted[0]["ChannelInfo"]["BleachingEnergy"] == 1980
    
    # Check second channel
    assert extracted[1]["Channel"] == "PE"
    assert extracted[1]["ChannelInfo"]["BleachingEnergy"] == 840
    
    # Check third channel
    assert extracted[2]["Channel"] == "APC"
    assert extracted[2]["ChannelInfo"]["BleachingEnergy"] == 780
    
    # Test with non-erase block (should return empty list)
    scan_block = data['procedures'][0]['blocks'][0]  # This should be a scan block
    result_non_erase = mp.get_erase_channel_info(scan_block)
    assert result_non_erase == []


def test_build_bucket_lookup():
    """Test that bucket lookup is built correctly."""
    bucket_lookup = mp.build_bucket_lookup(data)
    
    # Should return a dictionary (even if empty for our test data)
    assert isinstance(bucket_lookup, dict)
    
    # Test with minimal data structure that has proper reagent mappings
    test_data = {
        "procedures": [
            {
                "reagents": [
                    {"bucketId": "bucket1", "reagentId": {"itemId": "reagent1"}},
                    {"bucketId": "bucket2", "reagentId": {"itemId": "reagent2"}},
                ]
            }
        ],
        "reagents": [
            {
                "id": "reagent1",
                "antigen": "CD3",
                "clone": "Clone1",
                "exposureTime": 100,
                "supportedFixationMethods": ["PFA"],
                "antibody": "CD3_antibody",
                "antibodyType": "monoclonal",
                "hostSpecies": "mouse",
                "isotype": "IgG",
                "manufacturer": "TestCorp",
                "name": "CD3 Antibody",
                "orderNumber": "CD3-001",
                "species": "human"
            },
            {
                "id": "reagent2", 
                "antigen": "CD4",
                "clone": "Clone2",
                "exposureTime": 120,
                "supportedFixationMethods": ["PFA"],
                "antibody": "CD4_antibody",
                "antibodyType": "monoclonal",
                "hostSpecies": "rat",
                "isotype": "IgG2a",
                "manufacturer": "TestCorp",
                "name": "CD4 Antibody",
                "orderNumber": "CD4-001",
                "species": "human"
            }
        ]
    }
    
    lookup = mp.build_bucket_lookup(test_data)
    
    # Should have mappings for both buckets
    assert "bucket1" in lookup
    assert "bucket2" in lookup
    
    # Check bucket1 mapping
    bucket1_info = lookup["bucket1"]
    assert bucket1_info["antigen"] == "CD3"
    assert bucket1_info["clone"] == "Clone1"
    assert bucket1_info["exposureTime"] == 100
    assert bucket1_info["Antibody"] == "CD3_antibody"
    assert bucket1_info["Manufacturer"] == "TestCorp"
    
    # Check bucket2 mapping
    bucket2_info = lookup["bucket2"]
    assert bucket2_info["antigen"] == "CD4"
    assert bucket2_info["clone"] == "Clone2"
    assert bucket2_info["exposureTime"] == 120
    assert bucket2_info["AntibodyType"] == "monoclonal"


def test_process_experiment():
    """Test that experiment data is processed correctly with formatted headers."""
    experiment = data['experiments'][0]
    result = mp.process_experiment(experiment)
    
    # Check that result is a dictionary
    assert isinstance(result, dict)
    
    # Check that headers are formatted (have line breaks)
    expected_keys = [
        "Experiment\nName",
        "Start\nTime", 
        "End\nTime",
        "Running\nTime",
        "Used\nDisk\nSpace"
    ]
    
    for key in expected_keys:
        assert key in result
    
    # Check values
    assert result["Experiment\nName"] == "250128_liver_OCT_FCRB 1"
    assert result["Start\nTime"] == "2025-01-28T15:53:36Z"
    assert result["End\nTime"] == "2025-01-29T06:43:08Z"
    assert result["Running\nTime"] == "14h 49m 27s"
    assert result["Used\nDisk\nSpace"] == "182.645 KB"


def test_process_rois():
    """Test that ROI data is processed correctly with formatted headers."""
    roi = data['rois'][0]
    result = mp.process_rois(roi)
    
    # Check that result is a dictionary
    assert isinstance(result, dict)
    
    # Check that headers are formatted (have line breaks)
    expected_keys = [
        "ROI\nName",
        "Shape",
        "Height", 
        "Width",
        "Autofocus"
    ]
    
    for key in expected_keys:
        assert key in result
    
    # Check values
    assert result["ROI\nName"] == "C Overview"
    assert result["Shape"] == "Rectangle"
    assert result["Height"] == "10"
    assert result["Width"] == "19"
    assert result["Autofocus"] == "ImageBased"
    
    # Test with second ROI
    roi2 = data['rois'][1]
    result2 = mp.process_rois(roi2)
    assert result2["ROI\nName"] == "ROI 1"
    assert result2["Autofocus"] == "ConstantZ"


def test_process_sample():
    """Test that sample data is processed correctly with formatted headers."""
    sample = data['samples'][0]
    result = mp.process_sample(sample)
    
    # Check that result is a dictionary
    assert isinstance(result, dict)
    
    # Check that headers are formatted (have line breaks)
    expected_keys = [
        "Sample\nName",
        "Species",
        "Type",
        "Organ",
        "Fixation"
    ]
    
    for key in expected_keys:
        assert key in result
    
    # Check values
    assert result["Sample\nName"] == "250128_liver_OCT_FCRB"
    assert result["Species"] == "Human"
    assert result["Type"] == "Tissue"
    assert result["Organ"] == "Liver"
    assert result["Fixation"] == "PFA"


def test_process_block_column_order():
    """Test that block processing maintains the correct column order."""
    bucket_lookup = mp.build_bucket_lookup(data)
    
    # Test with a RunCycle block
    run_cycle_block = data['procedures'][0]['blocks'][5]  # RunCycle block
    result = mp.process_block(run_cycle_block, bucket_lookup)
    
    # Should return a list of dictionaries
    assert isinstance(result, list)
    assert len(result) > 0
    
    # Check that columns are in the correct order
    expected_order = [
        "Run\nCycle\nNumber", "Block\nType", "Antigen", "Channel", "Magnification",
        "Clone", "Dilution\nFactor", "Incubation\nTime", "Reagent\nExposure",
        "Coefficient", "Actual\nExposure", "Erasing\nMethod", "Bleaching\nEnergy", "Bleaching\nTime",
        "Validated\nFor", "Antibody", "Antibody\nType", "Host\nSpecies", "Isotype",
        "Manufacturer", "Order\nNumber", "Species", "Name"
    ]
    
    actual_columns = list(result[0].keys())
    assert actual_columns == expected_order
    
    # Test with a non-RunCycle block
    scan_block = data['procedures'][0]['blocks'][0]  # Scan block
    result_scan = mp.process_block(scan_block, bucket_lookup)
    
    # Should have the same column order (with most columns empty)
    actual_columns_scan = list(result_scan[0].keys())
    assert actual_columns_scan == expected_order


def test_bleaching_time_extraction():
    """Test that bleaching time is extracted correctly from reagents."""
    bucket_lookup = mp.build_bucket_lookup(data)
    
    # Test with RunCycle block that has bleaching time data
    run_cycle_block = data['procedures'][0]['blocks'][5]  # RunCycle block
    extracted = mp.get_run_cycle_channel_info(run_cycle_block, bucket_lookup)
    
    # Should return a list of channel info dictionaries
    assert isinstance(extracted, list)
    assert len(extracted) == 5  # DAPI, FITC, PE, APC, Vio780
    
    # Check bleaching time values for each channel
    channel_bleaching_times = {
        "DAPI": 0,      # DetectionChannel_1
        "FITC": 15,     # DetectionChannel_2  
        "PE": 20,       # DetectionChannel_3
        "APC": 25,      # DetectionChannel_4
        "Vio780": 0     # DetectionChannel_5
    }
    
    for channel_data in extracted:
        channel_name = channel_data["Channel"]
        expected_bleaching_time = channel_bleaching_times[channel_name]
        actual_bleaching_time = channel_data["ChannelInfo"]["BleachingTime"]
        
        assert actual_bleaching_time == expected_bleaching_time, \
            f"Channel {channel_name}: expected BleachingTime {expected_bleaching_time}, got {actual_bleaching_time}"
    
    # Test that BleachingTime field exists in all channels
    for channel_data in extracted:
        assert "BleachingTime" in channel_data["ChannelInfo"], \
            f"BleachingTime field missing in channel {channel_data['Channel']}"
