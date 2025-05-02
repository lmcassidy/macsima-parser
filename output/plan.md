
| Step                                    | What to do                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Where (file / function)                      | Tips                                                                                        |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------- |
| **1. Freeze the spec**                  | Make a small “mapping sheet” that lists every column you want, its friendly name, and the JSON path(s) it comes from.                                                                                                                                                                                                                                                                                                                                           | *new file* `column_map.md` (or Excel/Notion) | Having this in writing keeps refactors calm.                                                |
| **2. Tighten `parse_experiment_level`** | *•* Return **three** objects even on empty input (e.g., `({},[],[])`) so tests don’t explode.<br>*•* Compute `usedDiskspace_gb = raw / 1024**3` and format with `f"{…:.2f}"`.<br>*•* Join multiple racks with commas.<br>*•* Populate ROI & sample sub‑tables exactly as spec.                                                                                                                                                                                  | `macsima_parser.py`                          | Update unit‑test `test_parse_helpers_with_missing_data` accordingly.                        |
| **3. Rewrite `parse_blocks`**           | *•* Skip **Restain Nuclei** (`ProtocolBlockType_RestainNuclei`).<br>*•* For **Scan** blocks pull `magnification` and enabled channels (strip `FluorochromeType_`).<br>*•* For **Erase** blocks add `Bleaching Energy` per enabled channel (units: KJ).                                                                                                                                                                                                          | same                                         | Keep block order by index so you can label “Block 1 …”.                                     |
| **4. Expand `parse_run_cycles`**        | 1. Detect **each** `ProtocolBlockType_RunCycle`<br>2. For each detection‑channel (DAPI, FITC, PE, APC)…<br> a. Look up its `bucketId` → reagent in top‑level `reagents` to fetch Antigen, Clone, Exposure Time, Supported Fixation, etc.<br> b. Compute `Actual Exposure = exposureTime * timeCoefficient/100`.<br>3. Inject a **synthetic DAPI row every *nth* cycle** using the `repeatEveryNthCycle` from the Restain‑Nuclei block (cycle 8 in your sample). | same                                         | Store Restain‑Nuclei settings when you skip that block in step 3, then reference them here. |
| **5. Excel writer polish**              | *•* Write each DataFrame to named sheets: “Experiment Info”, “ROIs”, “Samples”, “Procedure Blocks”, “Run Cycles”.<br>*•* After `to_excel`, set portrait: `worksheet.set_portrait()`.<br>*•* Autofit or set column widths (optional).                                                                                                                                                                                                                            | `main()`                                     | Your dummy‑writer unit‑test will still pass because the API stays the same.                 |
| **6. New unit tests**                   | • `test_run_cycle_mapping()` – assert antigen/clone lookup via bucketId.<br>• `test_dapi_injection()` – JSON miniature with Restain every 3 cycles → verify DAPI appears on cycles 3, 6, …<br>• `test_diskspace_conversion()` – confirm bytes→GB rounding.                                                                                                                                                                                                      | `test_macsima_parser.py`                     | Use tiny inline JSON snippets; no need for full file.                                       |
| **7. Add coverage check**               | Run: `pytest --cov=macsima_parser --cov-report=term-missing`                                                                                                                                                                                                                                                                                                                                                                                                    |                                              | Aim for ≥ 90 % lines on the three parse functions.                                          |
| **8. Manual smoke test**                | `python macsima_parser.py data/250128_macsima_output.json output/report.xlsx` then open Excel and spot‑check against your spec.                                                                                                                                                                                                                                                                                                                                 | CLI                                          | Validate column names, units, DAPI cycles, portrait print preview.                          |
| **9. Cleanup / docs**                   | • Update `README.md` with “How to run” & sample output.<br>• Freeze dependencies in `requirements.txt`.                                                                                                                                                                                                                                                                                                                                                         | root                                         | `pip freeze > requirements.txt` (inside the env) is fine.                                   |

---

### Quick Code Fragments for the Key Fixes

```python
# parse_experiment_level – safe triple‑return
def parse_experiment_level(data):
    experiments = data.get("experiments", [])
    if not experiments:
        return {}, [], []              # ← avoid ValueError in tests
    ...
```

```python
# parse_blocks – skip Restain
for i, block in enumerate(procedure_blocks, 1):
    btype = block.get("blockType")
    if btype == "ProtocolBlockType_RestainNuclei":
        restain_info = block          # save repeatEveryNthCycle etc.
        continue                      # ← skip listing
    ...
```

```python
# parse_run_cycles – DAPI injection
repeat_n = restain_info.get("repeatEveryNthCycle", 8)
if ch == "DAPI" and (cycle_count % repeat_n == 0):
    # use restain_info values rather than reagent lookup
```

Follow that checklist and the workbook should match your “expected output” mock‑up precisely. Let me know if you’d like sample code for any step in more detail—or if you prefer I start by shipping a refactored `parse_run_cycles` right away.
