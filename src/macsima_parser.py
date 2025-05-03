from __future__ import annotations
import os
import json
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Union, IO

JsonFile = Union[str, Path, IO[str]]

def load_json(json_file: JsonFile) -> Any:
    """
    Load data from a JSON file.

    Parameters
    ----------
    json_file : str | pathlib.Path | IO[str]
        Path to a *.json* file (or an already‑opened text file handle).

    Returns
    -------
    Any
        Whatever `json.load` produces—usually `dict[str, Any]` or
        `list[Any]`, depending on the file’s contents.
    """
    # If a path‑like object was supplied, open it; otherwise assume it's a file‑like object
    if isinstance(json_file, (str, Path)):
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)
    else:                                   # file handle already open
        return json.load(json_file)
    

# --------------------------------------------------
# Experiment info helper functions
# --------------------------------------------------

def get_experiment_name(experiment: dict[str, Any]) -> str:
    """Returns the experiment name."""
    # NOTE: assume only one experiment in the file
    return experiment.get("name", "Unknown experiment")


def get_procedure_name(procedure: dict[str, Any]) -> str:
    """Returns the procedure name."""
    # NOTE: assume only one procedure in the file
    return procedure.get("comment", "Unknown procedure")

def get_rack_name(rack: list[dict[str, Any]]) -> str:
    """Returns the rack name."""
    return rack.get("name", "Unknown rack")

def get_start_time(experiment: dict) -> str:
    """Return the experiment's start time as an RFC 3339 string with 'Z'."""
    # assuming the raw string is already in ISO‑8601 / RFC 3339 form
    raw: str = experiment.get("executionStartDateTime", "Unknown end time")

    # Parse it so you know it’s valid
    dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))

    # Force UTC and format with a literal 'Z'
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def get_end_time(experiment: dict[str]) -> str:
    """Returns the experiment end time."""
    raw: str = experiment.get("executionEndDateTime", "Unknown end time")

    # Parse it so you know it’s valid
    dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))

    # Force UTC and format with a literal 'Z'
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def convert_seconds_to_hms(seconds):
    """Convert total seconds to (hours, minutes, seconds)."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    sec_left = seconds % 60
    return hours, minutes, sec_left

def get_running_time(experiment: dict[str, Any]) -> str:
    """Returns the experiment running time."""
    actual_running_time_s = experiment.get('actualRunningTime', 0)
    h, m, s = convert_seconds_to_hms(actual_running_time_s)
    runtime_str = f"{h}h {m}m {s}s"
    return runtime_str


def get_used_disk_space(experiment: dict) -> str:
    """
    Return the experiment's used‑disk‑space value as a string like '178.364 KB'.

    The JSON stores the size in bytes, so we convert to kilobytes (KiB = 1024 bytes)
    and round to three decimal places.
    """
    # raw number of **bytes**
    raw_bytes: int | float = experiment["usedDiskspace"]

    kib: float = raw_bytes / 1000                       # → KiB
    kib_rounded: float = round(kib, 3)                  # keep 3 decimal places
    return f"{kib_rounded:.3f} KB"

# TODO: add a function to get the used disk space in GB

# --------------------------------------------------
# ROI helper functions
# --------------------------------------------------

def get_roi_name(roi: dict[str, Any]) -> str:
    """Returns the ROI name."""
    return roi.get("name", "Unknown ROI")

def get_roi_shape_type(roi: dict[str, Any]) -> str:
    """return the ROI shape type."""
    shape = roi.get("shape", "Unknown shape")
    shape_type = shape.get("Type", "Unknown shape type")
    # remove prefix "ShapeType_"
    shape_type = shape_type.replace("ShapeType_", "")
    return shape_type

def get_roi_shape_height(roi):
    """Returns the ROI shape height."""
    try:
        shape_data_str = roi.get('shape', {}).get('Data', '{}')
        shape_data = json.loads(shape_data_str)
        height = shape_data.get('Height')
    except (json.JSONDecodeError, TypeError) as e:
        height = "Unknown height"
        print(f"Error decoding JSON or accessing height: {e}")
    return str(height)

def get_roi_shape_width(roi):
    """Returns the ROI shape width."""
    try:
        shape_data_str = roi.get('shape', {}).get('Data', '{}')
        shape_data = json.loads(shape_data_str)
        width = shape_data.get('Width')
    except (json.JSONDecodeError, TypeError) as e:
        width = "Unknown width"
        print(f"Error decoding JSON or accessing width: {e}")
    return str(width)

def get_autofocus_method(roi: dict[str, Any]) -> str:
    """Returns the autofocus method."""
    autofocus_method = roi.get("autoFocus", "Unknown autofocus method").get("method", "Unknown autofocus method")
    autofocus_method = autofocus_method.replace("AutofocusMethod_", "")
    return autofocus_method


# --------------------------------------------------
# Sample helper functions
# --------------------------------------------------

def get_sample_name(sample: dict[str, Any]) -> str:
    """Return sample name."""
    return sample.get("name", "Unknown sample")

def get_sample_species(sample: dict[str, Any]) -> str:
    """Return sample species."""
    return sample.get("species", "Unknown species")

def get_sample_type(sample: dict[str, Any]) -> str:
    """Return sample type."""
    sample_type = sample.get("sampleType", "Unknown sample type")
    # remove prefix "SampleType_"
    sample_type = sample_type.replace("SampleType_", "")
    return sample_type

def get_sample_organ(sample: dict[str, Any]) -> str:
    """Return sample organ."""
    return sample.get("organ", "Unknown organ")

def get_sample_fixation_method(sample: dict[str, Any]) -> str:
    """Return sample fixation method."""
    return sample.get("fixationMethod", "Unknown fixation method")

# --------------------------------------------------
# Procedure block functions
# --------------------------------------------------

def add_numbers_to_run_cycles(blocks: dict[str, Any]) -> int:
    """Add numbers to run cycles."""
    run_cycle_number = 0
    for block in blocks:
        if block.get("protocolBlockType") == "protocolBlockType_RunCycle":
            run_cycle_number += 1
            block["runCycleNumber"] = run_cycle_number
    return block

def get_run_cycle_number(block: dict[str, Any]) -> int:
    """Return the run cycle number."""
    return block.get("runCycleNumber", 0)

def get_block_type(block: dict[str, Any]) -> str:
    """Return the block type."""
    return block.get("protocolBlockType", "Unknown block type")

def get_block_name(block: dict[str, Any]) -> str:
    """Return the block name."""
    return block.get("name", "Unknown block name")

def get_block_magnification(block: dict[str, Any]) -> str:
    """Return the block magnification."""
    return block.get("magnification", "Unknown magnification")

def get_erase_bleaching_energy(block: dict[str, Any]) -> str:   
    """Return the erase bleaching energy."""
    return block.get("bleachingEnergy", "Unknown bleaching energy")
    
def get_run_cycle_channel_info(block: dict[str, Any]) -> str:
    """Return the run cycle channel info."""
    return block.get("channels", "Unknown channel info")
    

    if __name__ == "__main__":
        data = load_json('../data/250128_macsima_output.json')
        experiements = data['experiments']
        racks = data['racks']
        rois = data['rois']
        samples = data['samples']
        procedures = data['procedures']