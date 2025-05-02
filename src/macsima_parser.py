import os
import json
import pandas as pd
from datetime import datetime, timedelta

def load_json(json_file):
    """Load data from a JSON file."""
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data

def convert_seconds_to_hms(seconds):
    """Convert total seconds to (hours, minutes, seconds)."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    sec_left = seconds % 60
    return hours, minutes, sec_left

def convert_bytes_to_gb(disk_usage_bytes):
    """If usedDiskspace is in bytes, convert to GB. 
       Adjust if your data is actually in kB, MB, etc.
    """
    return disk_usage_bytes / (1024**3)

def parse_experiment_level(data):
    """Extract top-level experiment info, ROI, sample, etc."""
    experiments = data.get('experiments', [])
    if not experiments:
        return {}

    exp_data = experiments[0]  # Usually one experiment, or take the first
    exp_name = exp_data.get('name', 'N/A')
    start_time = exp_data.get('executionStartDateTime', 'N/A')
    end_time = exp_data.get('executionEndDateTime', 'N/A')
    actual_running_time_s = exp_data.get('actualRunningTime', 0)
    used_diskspace_raw = exp_data.get('usedDiskspace', 0)

    # Convert runtime
    h, m, s = convert_seconds_to_hms(actual_running_time_s)
    runtime_str = f"{h}h {m}m {s}s"

    # Convert disk usage
    used_diskspace_gb = convert_bytes_to_gb(used_diskspace_raw)

    # Racks info (there may be multiple racks)
    rack_info = []
    for rack in data.get('racks', []):
        rack_info.append(rack.get('name', 'N/A'))

    # ROIs info – note you might have multiple
    rois_info = []
    for roi in data.get('rois', []):
        roi_type = roi.get('type', 'N/A')
        roi_shape = roi.get('shape', {})
        roi_auto_focus_method = roi.get('autoFocus', {}).get('method', 'N/A')
        rois_info.append({
            'ROI Type': roi_type,
            'ROI Shape': str(roi_shape),
            'Autofocus Method': roi_auto_focus_method
        })

    # Sample info – you might have multiple samples
    samples_info = []
    for samp in data.get('samples', []):
        samples_info.append({
            'Sample Name': samp.get('name', 'N/A'),
            'Species': samp.get('species', 'N/A'),
            'Sample Type': samp.get('sampleType', 'N/A'),
            'Organ': samp.get('organ', 'N/A'),
            'Fixation Method': samp.get('fixationMethod', 'N/A')
        })

    # Prepare a dictionary for "Experiment Info"
    experiment_dict = {
        'Experiment Name': exp_name,
        'Procedure Name': data.get('procedures', [{}])[0].get('comment', 'N/A'),
        'Rack(s)': ", ".join(rack_info),
        'Start Time': start_time,
        'End Time': end_time,
        'Running Time (h/m/s)': runtime_str,
        'Used Disk Space (GB)': f"{used_diskspace_gb:.2f}"
    }

    return experiment_dict, rois_info, samples_info

def parse_blocks(data):
    """Parse the procedure blocks (e.g., Scan, Define ROI, Erase, etc.)."""
    blocks_data = []
    procedures = data.get('procedures', [])
    if not procedures:
        return blocks_data

    # Usually there's a single procedure or you can iterate over multiple
    procedure_blocks = procedures[0].get('blocks', [])

    for i, block in enumerate(procedure_blocks, start=1):
        block_type = block.get('protocolBlockType', '')
        block_comment = block.get('comment', '')
        # Example fields
        magnification = block.get('magnification', 'N/A')
        is_enabled = block.get('isEnabled', True)

        # Channels might be embedded inside "detectionSettings" or "channels" 
        # depending on your actual JSON. For demonstration:
        channels = block.get('detectionSettings', [])
        # For bleaching info:
        bleaching_energy = block.get('bleachingEnergy', 'N/A')
        
        # If the block is "Erase," or "Bleach," or "Scan," etc., you can parse accordingly.
        # Also skip the "restain nuclei" block from top-level listing if you want:
        if block_type == "protocolBlockType_RestainNuclei":
            # Skip it here or handle separately
            continue

        blocks_data.append({
            'Block #': i,
            'Block Type': block_type,          # e.g. "protocolBlockType_Scan"
            'Block Name': block_comment,       # e.g. "Scan" or "Erase"
            'Magnification': magnification,
            'Bleaching Energy': bleaching_energy if block_type == "protocolBlockType_Erase" else '',
            'Is Enabled': is_enabled
        })

    return blocks_data

def parse_run_cycles(data):
    """
    Parse the actual run cycles ("run cycle" blocks).
    The user wants columns per channel: e.g., DAPI, FITC, PE, APC.
    Then rows for: antigen, clone, dilution factor, etc.
    """
    # We'll return a list of cycle dictionaries and then pivot them
    run_cycles_info = []

    procedures = data.get('procedures', [])
    if not procedures:
        return run_cycles_info

    # The "run cycles" might be in procedures[0]['blocks'] with 
    # protocolBlockType_Run or something similar. 
    # We'll need to figure out how your JSON structure labels them:
    procedure_blocks = procedures[0].get('blocks', [])

    # Reagents dictionary (by "bucketID" or some ID) to find antigen, clone, etc.
    reagents_info = {}
    for reagent in data.get('reagents', []):
        bucket_id = reagent.get('bucketId', 'N/A')
        # Some possible fields
        reagents_info[bucket_id] = {
            'Antigen': reagent.get('antigenName', 'N/A'),
            'Clone': reagent.get('clone', 'N/A'),
            'Exposure Time': reagent.get('exposureTime', 0),   # s
            'Supported Fixation': reagent.get('supportedFixationMethods', [])
        }

    # Let’s identify your channels (just an example).
    # You might have them globally or repeated in each block:
    known_channels = ["DAPI", "FITC", "PE", "APC"]  # or parse from the JSON

    cycle_count = 0
    for block in procedure_blocks:
        block_type = block.get('protocolBlockType', '')
        if block_type == 'protocolBlockType_RunCycle':
            cycle_count += 1
            # Now parse the run cycle details
            # For each channel, see if it was used, gather reagent info, etc.
            # Example: block['runs'] or block['channels'] might hold details

            # We might see something like block['runs'][0]['bucketId'] for the reagent used.
            # This is hypothetical code that you will need to adapt:
            channel_info = block.get('channels', [])  # or 'runs' or something else
            # Erasing / bleaching
            erasing_method = block.get('erasingMethod', 'N/A')
            bleaching_energy = block.get('bleachingEnergy', '')

            # Incubation time, dilution, etc. might come from the same or sub-structures:
            # for demonstration:
            incubation_time = block.get('incubationTime', 0)        # minutes
            dilution_factor = block.get('dilutionFactor', 1)
            time_coefficient = block.get('timeCoefficient', 100)     # e.g. 100%

            # We'll build a row for each known channel
            for ch in known_channels:
                # In your real data, you might see which reagent is associated with that channel
                # Or each channel might have its own sub-block. This is just an example:
                # Suppose we find the reagent bucket ID for this channel:
                bucket_id = block.get('bucketIdMapping', {}).get(ch, '')  # hypothetical
                if bucket_id and bucket_id in reagents_info:
                    antigen = reagents_info[bucket_id]['Antigen']
                    clone = reagents_info[bucket_id]['Clone']
                    base_exposure_time = reagents_info[bucket_id]['Exposure Time']
                    supported_fixation = reagents_info[bucket_id]['Supported Fixation']
                else:
                    antigen = "Not in this cycle"
                    clone = ""
                    base_exposure_time = 0
                    supported_fixation = []

                # Actual exposure = base exposure * time_coefficient/100
                actual_exposure = (base_exposure_time * time_coefficient) / 100.0

                run_cycles_info.append({
                    'Cycle #': cycle_count,
                    'Channel': ch,
                    'Antigen': antigen,
                    'Clone': clone,
                    'Dilution Factor': dilution_factor,
                    'Incubation Time (min)': incubation_time,
                    'Reagent Exposure Time (s)': base_exposure_time,
                    'Exposure Coefficient (%)': time_coefficient,
                    'Actual Exposure (s)': actual_exposure,
                    'Erasing Method': erasing_method,
                    'Bleaching Energy': bleaching_energy if erasing_method.lower() == 'bleach' else '',
                    'Validated For': ", ".join(supported_fixation)
                })

    return run_cycles_info

def main(json_path, output_excel):
    data = load_json(json_path)

    # 1) Parse experiment-level
    experiment_dict, rois_info, samples_info = parse_experiment_level(data)
    
    # 2) Convert that experiment dict to a one-row DataFrame for easier exporting:
    df_expt_info = pd.DataFrame([experiment_dict])

    # 3) Build DataFrame of ROI info:
    df_rois = pd.DataFrame(rois_info) if rois_info else pd.DataFrame()

    # 4) Build DataFrame of sample info:
    df_samples = pd.DataFrame(samples_info) if samples_info else pd.DataFrame()

    # 5) Parse top-level blocks (excluding the restain block):
    blocks_info = parse_blocks(data)
    df_blocks = pd.DataFrame(blocks_info)

    # 6) Parse run cycles in detail:
    run_cycles_info = parse_run_cycles(data)
    df_cycles = pd.DataFrame(run_cycles_info)

    # --- Write to Excel ---
    with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
        # Write each DataFrame to a sheet:
        df_expt_info.to_excel(writer, index=False, sheet_name='Experiment Info')
        if not df_rois.empty:
            df_rois.to_excel(writer, index=False, sheet_name='ROIs')
        if not df_samples.empty:
            df_samples.to_excel(writer, index=False, sheet_name='Samples')
        if not df_blocks.empty:
            df_blocks.to_excel(writer, index=False, sheet_name='Procedure Blocks')
        if not df_cycles.empty:
            df_cycles.to_excel(writer, index=False, sheet_name='Run Cycles')

        # Set portrait layout (via xlsxwriter):
        workbook  = writer.book
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            worksheet.set_paper(1)  # 1 = Letter portrait; 9 = A4 portrait
            # Also can set for printing:
            worksheet.set_portrait()  # explicitly portrait

if __name__ == "__main__":
    # Example usage:
    json_file = "data/250128_macsima_output.json"
    # if dir output does not exist, create it
    if not os.path.exists("output"):
        os.makedirs("output")
    output_file = "output/macsima_report.xlsx" # Desired Excel output
    main(json_file, output_file)
    print("Report generated:", output_file)
