from __future__ import annotations
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Union, IO, Dict, Tuple, Optional
import logging

# Basic configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()  # You can add FileHandler, SMTPHandler, etc.
    ]
)

logger = logging.getLogger(__name__)


JsonFile = Union[str, Path, IO[str]]


def get_input_path() -> Path:
    parser = argparse.ArgumentParser(description="MACSima JSON parser")
    parser.add_argument("json_path", nargs="?", type=Path, help="Path to input JSON file")
    args = parser.parse_args()

    if args.json_path and args.json_path.exists():
        return args.json_path

    # fallback: prompt the user
    path_str = input("Enter path to input JSON file: ").strip()
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {path}")
    return path

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

def convert_seconds_to_hms(seconds)-> Tuple[int, int, int]:
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
    raw_bytes: int | float = experiment.get("usedDiskspace")

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
        logger.warning(f"Error decoding JSON or accessing height: {e}")
    return str(height)

def get_roi_shape_width(roi):
    """Returns the ROI shape width."""
    try:
        shape_data_str = roi.get('shape', {}).get('Data', '{}')
        shape_data = json.loads(shape_data_str)
        width = shape_data.get('Width')
    except (json.JSONDecodeError, TypeError) as e:
        width = "Unknown width"
        logger.warning(f"Error decoding JSON or accessing width: {e}")
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

def add_numbers_to_run_cycles(blocks: dict[str, Any]) -> dict[str, Any]:
    """Add numbers to run cycles."""
    run_cycle_number = 0
    updated_blocks = []
    for i, block in enumerate(blocks):
        if block.get("blockType") == "ProtocolBlockType_RunCycle":
            run_cycle_number += 1
            logger.debug(f"Adding run cycle number {run_cycle_number} to block {i}")
            block["runCycleNumber"] = run_cycle_number
        updated_blocks.append(block)
    return updated_blocks

def get_run_cycle_number(block: dict[str, Any]) -> int:
    """Return the run cycle number."""
    logger.debug(f"Block keys: {block.keys()}")
    return block.get("runCycleNumber", "Unknown run cycle number")

def get_block_type(block: dict[str, Any]) -> str:
    """Return the block type."""
    block_type = block.get("blockType", "Unknown block type")
    # remove prefix "ProtocolBlockType_"
    if block_type.startswith("ProtocolBlockType_"):
        block_type = block_type.replace("ProtocolBlockType_", "")
    return block_type

def get_block_name(block: dict[str, Any]) -> str:
    """Return the block name."""
    return block.get("name", "Unknown block name")

def get_block_magnification(block: dict[str, Any]) -> str:
    """Return the block magnification."""
    logger.debug(f"Block keys: {block.keys()}")
    return block.get("magnification", "N/A")

def get_erase_bleaching_energy(block: dict[str, Any]) -> list[dict[str, Any]] | str:
    if block.get("blockType") != "ProtocolBlockType_Erase":
        return "N/A"
    
    results = []
    channels = block.get("photos", {})
    
    for channel in channels.values():
        fluor = channel.get("fluorochromeType")
        energy = channel.get("bleachingEnergy")
        enabled = channel.get("isEnabled", False)
        
        if enabled and fluor and fluor != "FluorochromeType_None" and energy:
            label = fluor.split("_")[-1]  # FluorochromeType_APC → APC
            results.append({"Channel": label, "bleachingEnergy": energy})
    
    return results if results else "N/A"

def get_erase_channel_info(block: dict[str, Any]) -> list[dict]:
    """
    Return a list like
        [
          {"Channel": "FITC", "ChannelInfo": {"BleachingEnergy": 1980}},
          {"Channel": "PE",   "ChannelInfo": {"BleachingEnergy": 840}},
          ...
        ]
    Only channels where *isEnabled* is true are listed.
    """
    out = []
    for dc in block.get("photos", {}).values():
        if (
            dc.get("isEnabled") 
            and dc.get("fluorochromeType") != "FluorochromeType_None"
        ):
            label = dc["fluorochromeType"].split("_")[-1]   # …_APC → APC
            out.append(
                {
                    "Channel": label,
                    "ChannelInfo": {"BleachingEnergy": dc.get("bleachingEnergy", "")},
                }
            )
    return out

  
def get_run_cycle_channel_info(block: dict, bucket_lookup: dict) -> list[dict]:
    """
    Build a run-cycle channel summary for one ProtocolBlockType_RunCycle block.
    Returns a list ordered DAPI ▸ FITC ▸ PE ▸ APC ▸ Vio780.
    """
    channel_order = [
        ("DetectionChannel_1", "DAPI"),
        ("DetectionChannel_2", "FITC"),
        ("DetectionChannel_3", "PE"),
        ("DetectionChannel_4", "APC"),
        ("DetectionChannel_5", "Vio780"),
    ]
    # Full field set (add more as needed)
    FIELDNAMES = [
        "Antigen", "Clone", "DilutionFactor", "IncubationTime", "ReagentExposureTime",
        "ExposureCoefficient", "ActualExposureTime", "ErasingMethod", "BleachingEnergy", "ValidatedFor",
        "Antibody", "AntibodyType", "HostSpecies", "Isotype", "Manufacturer", "Name", "OrderNumber", "Species"
    ]

    out: list[dict] = []
    dct_reagents = block.get("reagents", {})
    if not dct_reagents:
        logger.warning("No reagents found in RunCycle block")
        return out

    for key, chan_name in channel_order:
        dc = dct_reagents.get(key, {})
        chan_dict = {"Channel": chan_name}
        # Build a dict with all keys, defaulting to ""
        chan_info = {f: "" for f in FIELDNAMES}
        bucket_id = dc.get("bucketId", "")
        if bucket_id:
            reagent = bucket_lookup.get(bucket_id, {})
            # Fill from dc and reagent as before
            chan_info.update({
                "Antigen": reagent.get("antigen", ""),
                "Clone": reagent.get("clone", ""),
                "DilutionFactor": dc.get("dilutionFactor", ""),
                "IncubationTime": dc.get("incubationTime", ""),
                "ReagentExposureTime": reagent.get("exposureTime", ""),
                "ExposureCoefficient": dc.get("exposureTimeAndCoefficient", {}).get("timeCoefficient", ""),
                "ActualExposureTime": (
                    reagent.get("exposureTime", 0) * dc.get("exposureTimeAndCoefficient", {}).get("timeCoefficient", 0) / 100
                    if reagent.get("exposureTime") and dc.get("exposureTimeAndCoefficient") else ""
                ),
                "ErasingMethod": dc.get("erasingMethod", "").split("_")[-1] if dc.get("erasingMethod") else "",
                "BleachingEnergy": dc.get("bleachingEnergy", ""),
                "ValidatedFor": reagent.get("supportedFixationMethods", ""),
                "Antibody": reagent.get("Antibody", ""),
                "AntibodyType": reagent.get("AntibodyType", ""),
                "HostSpecies": reagent.get("HostSpecies", ""),
                "Isotype": reagent.get("Isotype", ""),
                "Manufacturer": reagent.get("Manufacturer", ""),
                "Name": reagent.get("Name", ""),
                "OrderNumber": reagent.get("OrderNumber", ""),
                "Species": reagent.get("Species", ""),
            })
        chan_dict["ChannelInfo"] = chan_info
        out.append(chan_dict)
    return out


def build_bucket_lookup(data: dict) -> Dict[str, Dict[str, Any]]:
    """
    Map bucketId  ->  reagent metadata (antigen, clone, exposureTime, …)
    """
    # map bucketId ➜ reagent UUID (comes from the procedure)
    bucket_to_reagent_id: Dict[str, str] = {}
    for proc in data.get("procedures", []):
        for link in proc.get("reagents", []):
            bid  = link.get("bucketId")
            rid  = link.get("reagentId", {}).get("itemId")
            if bid and rid:
                bucket_to_reagent_id[bid] = rid

    #  map reagent UUID ➜ metadata (comes from the global catalogue)
    catalogue: Dict[str, Dict[str, Any]] = {
        r["id"]: {
            "antigen":      r.get("antigen",  "Unknown"),
            "clone":        r.get("clone",    "N/A"),
            "exposureTime": r.get("exposureTime", 0),
            "supportedFixationMethods": r.get("supportedFixationMethods", ""),
            "Antibody":         r.get("antibody", ""),
            "AntibodyType":     r.get("antibodyType", ""),
            "HostSpecies":      r.get("hostSpecies", ""),
            "Isotype":          r.get("isotype", ""),
            "Manufacturer":     r.get("manufacturer", ""),
            "Name":             r.get("name", ""),
            "OrderNumber":      r.get("orderNumber", ""),
            "Species":          r.get("species", ""),
        }
        for r in data.get("reagents", [])
    }

    return {bid: catalogue.get(rid, {}) for bid, rid in bucket_to_reagent_id.items()}


# ------------------------------------------------------------------ #
#  Query helpers
# ------------------------------------------------------------------ #
def get_antigen_clone_by_bucket(bucket_id: str,
                                bucket_lookup: Dict[str, Dict[str, str]]
                               ) -> Optional[Tuple[str, str]]:
    """
    Fast O(1) lookup using the pre-built dictionary.
    Returns (antigen, clone)  or  None if the bucket is unknown.
    """
    info = bucket_lookup.get(bucket_id)
    if info is None:
        return None
    return info["Antigen"], info["Clone"]


def get_antigen_clone_by_reagent_id(reagent_uuid: str,
                                    data: dict
                                   ) -> Optional[Tuple[str, str]]:
    """
    Directly fetch antigen / clone when you already have the reagent UUID.
    Scans the global reagent catalogue only once per call.
    """
    for reagent in data.get("reagents", []):
        if reagent.get("id") == reagent_uuid:
            return reagent.get("antigen", "Unknown"), reagent.get("clone", "N/A")
    return None

def process_experiment(experiment: dict[str, Any]) -> dict[str, Any]:
    return {
        "ExperimentName":  get_experiment_name(experiment),
        "StartTime":       get_start_time(experiment),
        "EndTime":         get_end_time(experiment),
        "RunningTime":     get_running_time(experiment),
        "UsedDiskSpace":   get_used_disk_space(experiment),
    }

def process_rois(roi: dict[str, Any]) -> dict[str, Any]:
    return {
        "ROIName":    get_roi_name(roi),
        "Shape":      get_roi_shape_type(roi),
        "Height":     get_roi_shape_height(roi),
        "Width":      get_roi_shape_width(roi),
        "Autofocus":  get_autofocus_method(roi),
    }

def process_sample(sample: dict[str, Any]) -> dict[str, Any]:
    return {
        "SampleName":   get_sample_name(sample),
        "Species":      get_sample_species(sample),
        "Type":         get_sample_type(sample),
        "Organ":        get_sample_organ(sample),
        "Fixation":     get_sample_fixation_method(sample),
    }

def process_block(block: dict[str, Any],
                  bucket_lookup: dict[str, Any]) -> list[dict[str, Any]]:
    common = {
        "BlockName":     get_block_name(block),
        "BlockType":     get_block_type(block),
        "Magnification": get_block_magnification(block),
        "RunCycleNumber": (
            get_run_cycle_number(block) if get_block_type(block) == "RunCycle" else ""
        ),
    }

    # ---------- ERASE blocks -----------------------------------
    if common["BlockType"] == "Erase":
        rows = []
        for chan in get_erase_channel_info(block):
            rows.append(
                {
                    **common,
                    "Channel":         chan["Channel"],
                    "BleachingEnergy": chan["ChannelInfo"]["BleachingEnergy"],
                }
            )
        return rows                         # <- finished for Erase

    # ---------- Non-run-cycle  (Scan, DefineROIs, …) -------------
    if common["BlockType"] != "RunCycle":
        return [common]

    # ---------- RUN-CYCLE blocks --------------------------------
    rows = []
    for chan in get_run_cycle_channel_info(block, bucket_lookup):
        cc = chan["ChannelInfo"]
        rows.append(
            {
                **common,
                "Channel":         chan["Channel"],
                "Antigen":         cc.get("Antigen", ""),
                "Clone":           cc.get("Clone", ""),
                "DilutionFactor":  cc.get("DilutionFactor", ""),
                "IncubationTime":  cc.get("IncubationTime", ""),
                "ReagentExposure": cc.get("ReagentExposureTime", ""),
                "Coefficient":     cc.get("ExposureCoefficient", ""),
                "ActualExposure":  cc.get("ActualExposureTime", ""),
                "ErasingMethod":   cc.get("ErasingMethod", ""),
                "BleachingEnergy": cc.get("BleachingEnergy", ""),
                "ValidatedFor":    cc.get("ValidatedFor", ""),
                "Antibody": cc.get("Antibody"),
                "AntibodyType": cc.get("AntibodyType"),
                "HostSpecies": cc.get("HostSpecies"),
                "Isotype": cc.get("Isotype"),
                "Manufacturer": cc.get("Manufacturer"),
                "Name": cc.get("Name"),
                "OrderNumber": cc.get("OrderNumber"),
                "Species": cc.get("Species")


            }
        )
    return rows


if __name__ == "__main__":
    json_path = get_input_path()
    logger.info(f"Loading JSON: {json_path}")
    data          = load_json(json_path)
    bucket_lookup = build_bucket_lookup(data)

    # ---------- gather rows ------------------------------------
    exp_rows    = [process_experiment(e) for e in data["experiments"]]
    rack_rows   = [{"RackName": get_rack_name(r)} for r in data["racks"]]
    roi_rows    = [process_rois(r)       for r in data["rois"]]
    sample_rows = [process_sample(s)     for s in data["samples"]]

    block_rows: list[dict] = []
    for proc in data["procedures"]:
        # add run-cycle numbers once
        blocks = add_numbers_to_run_cycles(proc["blocks"])
        for b in blocks:
            block_rows.extend(process_block(b, bucket_lookup))

    # ---------- to Excel ---------------------------------------
    out_xlsx = json_path.with_suffix(".xlsx")
    logger.info(f"Writing Excel report ➜ {out_xlsx}")

    import pandas as pd
    with pd.ExcelWriter(out_xlsx, engine="xlsxwriter") as xls:
        pd.DataFrame(exp_rows   ).to_excel(xls, sheet_name="Experiment", index=False)
        pd.DataFrame(rack_rows  ).to_excel(xls, sheet_name="Racks",      index=False)
        pd.DataFrame(roi_rows   ).to_excel(xls, sheet_name="ROIs",       index=False)
        pd.DataFrame(sample_rows).to_excel(xls, sheet_name="Samples",    index=False)

        # big table of all blocks & channels
        pd.DataFrame(block_rows ).to_excel(xls, sheet_name="Blocks",     index=False)

    logger.info("✅ Excel report created successfully.")
