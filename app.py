from flask import Flask, request, send_file, render_template, flash, redirect, url_for
import os
import tempfile
from pathlib import Path
from werkzeug.utils import secure_filename
import logging

# Import your existing parser
from src.macsima_parser import load_json, build_bucket_lookup, process_experiment, process_rois, process_sample, process_block, add_numbers_to_run_cycles, propagate_magnification, add_blank_lines_between_run_cycles, get_rack_name
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this to a random secret key
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'json'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_json_to_excel(json_file_path):
    """Process JSON file and return Excel file path"""
    logger.info(f"Processing JSON file: {json_file_path}")
    
    try:
        # Load and process the JSON data
        data = load_json(json_file_path)
        bucket_lookup = build_bucket_lookup(data)

        # Gather rows
        exp_rows = [process_experiment(e) for e in data["experiments"]]
        rack_rows = [{"RackName": get_rack_name(r)} for r in data["racks"]]
        roi_rows = [process_rois(r) for r in data["rois"]]
        sample_rows = [process_sample(s) for s in data["samples"]]

        block_rows = []
        for proc in data["procedures"]:
            blocks = add_numbers_to_run_cycles(proc["blocks"])
            blocks = propagate_magnification(blocks)
            for b in blocks:
                block_rows.extend(process_block(b, bucket_lookup))

        # Add blank lines between different run cycles
        block_rows = add_blank_lines_between_run_cycles(block_rows)

        # Create Excel file
        excel_path = Path(json_file_path).with_suffix(".xlsx")
        
        with pd.ExcelWriter(excel_path, engine="xlsxwriter") as xls:
            pd.DataFrame(exp_rows).to_excel(xls, sheet_name="Experiment", index=False)
            pd.DataFrame(rack_rows).to_excel(xls, sheet_name="Racks", index=False)
            pd.DataFrame(roi_rows).to_excel(xls, sheet_name="ROIs", index=False)
            pd.DataFrame(sample_rows).to_excel(xls, sheet_name="Samples", index=False)
            pd.DataFrame(block_rows).to_excel(xls, sheet_name="Blocks", index=False)

        logger.info(f"Excel report created successfully: {excel_path}")
        return str(excel_path)
        
    except Exception as e:
        logger.error(f"Error processing JSON file: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        temp_json_path = None
        excel_path = None
        try:
            # Create temporary file for uploaded JSON
            with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_json:
                temp_json_path = temp_json.name
                file.save(temp_json_path)
                
            # Process the JSON file
            excel_path = process_json_to_excel(temp_json_path)
            
            # Send the Excel file to user
            response = send_file(
                excel_path,
                as_attachment=True,
                download_name=f"{Path(file.filename).stem}_report.xlsx",
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            # Schedule cleanup after response is sent
            @response.call_on_close
            def cleanup():
                try:
                    if temp_json_path and os.path.exists(temp_json_path):
                        os.unlink(temp_json_path)
                    if excel_path and os.path.exists(excel_path):
                        os.unlink(excel_path)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temporary files: {e}")
            
            return response
                
        except Exception as e:
            # Cleanup on error
            try:
                if temp_json_path and os.path.exists(temp_json_path):
                    os.unlink(temp_json_path)
                if excel_path and os.path.exists(excel_path):
                    os.unlink(excel_path)
            except:
                pass
            
            # Provide user-friendly error messages
            error_message = get_user_friendly_error_message(e, file.filename)
            flash(error_message)
            return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload a JSON file.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)