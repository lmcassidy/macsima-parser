
## 1 · Experiment Info (sheet **“Experiment Info”**)

| Excel column (friendly name) | JSON path / rule                                        | Notes                               |
| ---------------------------- | ------------------------------------------------------- | ----------------------------------- |
| `Experiment Name`            | `experiments[0].name`                                   | first (and only) experiment block   |
| `Procedure Name`             | `procedures[0].comment`           | “Standard procedure” in sample      |
| `Rack(s)`                    | `racks[*].name → join(", ")`                            | comma‑separate if >1                |
| `Start Time`                 | `experiments[0].executionStartDateTime`                 | ISO‑8601 UTC                        |
| `End Time`                   | `experiments[0].executionEndDateTime`                   |  –                                  |
| `Running Time (h/m/s)`       | `experiments[0].actualRunningTime (seconds) → hh mm ss` | `timedelta(seconds=...)`            |
| `Used Disk Space (GB)`       | `experiments[0].usedDiskspace / 1024**3 → 2 dp`         | unknown unit → assume bytes for now |

---

## 2 · ROIs (sheet **“ROIs”**) element 0 is the whole area and after that is the zoom in

| Excel column       | JSON path / rule           | Notes                       |
| ------------------ | -------------------------- | --------------------------- |
| `ROI Type`         | `rois[*].shape.Type`       | strip `"ShapeType_"` prefix |
| `ROI Dimensions`   | `data['rois'][*]['shape']['Data']`| extract_roi_dimensions(data['rois'])
| `Autofocus Method` | `rois[*].autoFocus.method` | strip `"AutofocusMethod_"`  |

---

## 3 · Samples (sheet **“Samples”**)

| Excel column      | JSON path / rule            | Notes                        |
| ----------------- | --------------------------- | ---------------------------- |
| `Sample Name`     | `samples[*].name`           | links to ROI via `sampleIds` |
| `Species`         | `samples[*].species`        | e.g. human                         |
| `Sample Type`     | `samples[*].sampleType`     | strip  '`"SampleType_"`        |
| `Organ`           | `samples[*].organ`          | e.g. liver                          |
| `Fixation Method` | `samples[*].fixationMethod` | e.g. `"PFA"`           |

---

## 4 · Procedure Blocks (sheet **“Procedure Blocks”**)

| Excel column            | JSON path / rule                                          | Notes                                         |
| ----------------------- | --------------------------------------------------------- | --------------------------------------------- |
| `Block #`               | order in `procedures[0].blocks` (1‑based)                 | after filtering                               |
| `Block Type`            | `block.blockType` → strip prefix                          | e.g. `Scan`, `Erase`                          |
| `Block Name`            | `block.comment ?? block.name`                             | –                                             |
| `Magnification`         | `block.magnification`                                     | “N/A” if missing                              |
| `Bleaching Energy (KJ)` | `block.photos.*.bleachingEnergy` (Erase only); else blank | multiple channels – join “DAPI:0; FITC:1980…” |
| `Is Enabled`            | `block.isEnabled`                                         | boolean                                       |

> **Filter rules:**
> • Skip blocks of type `ProtocolBlockType_RestainNuclei` (saved for run‑cycle injection).
> • Preserve original order so “Block #” matches machine log.

---

## 5 · Run Cycles (sheet **“Run Cycles”**)

| Excel column                | JSON path / rule                                                                         | Notes                  |
| --------------------------- | ---------------------------------------------------------------------------------------- | ---------------------- |
| `Run Cycle #`               | sequential over blocks where `blockType == "ProtocolBlockType_RunCycle"`                 | –                      |
| `Channel`                   | detection‑channel name (`fluorochromeType` → strip prefix)                               | DAPI, FITC, PE, APC    |
| `Antigen`                   | find `bucketId` in current channel → look up **top‑level** `reagents[*].id` → `.antigen` | blank for DAPI/restain |
| `Clone`                     | same lookup → `.clone`                                                                   | blank possible         |
| `Dilution Factor`           | channel.`dilutionFactor`                                                                 | integer                |
| `Incubation Time (min)`     | channel.`incubationTime`                                                                 | –                      |
| `Reagent Exposure Time (s)` | reagent.`exposureTime` (from lookup)                                                     | –                      |
| `Exposure Coefficient (%)`  | channel.`exposureTimeAndCoefficient.timeCoefficient`                                     | –                      |
| `Actual Exposure Time (s)`  | `exposureTime * coefficient / 100`                                                       | float                  |
| `Erasing Method`            | channel.`erasingMethod` → strip prefix                                                   | –                      |
| `Bleaching Energy`          | channel.`bleachingEnergy`                                                                | 0 for none             |
| `Validated For`             | reagent.`supportedFixationMethods`                                                       | may be CSV             |

> **Special rule – Restain nuclei injection**
> Every `restain.repeatEveryNthCycle` cycles (8 in sample) **prepend** a DAPI row that re‑uses the dilution, incubation & exposure settings from the `RestainNuclei` block.

---

### Legend

* **JSON path notation:** Feel free to translate to `dict.get()` chains or `jsonpath_ng`—this doc is for humans.
* “Strip prefix” means turn `"FluorochromeType_DAPI"` → `"DAPI"`, `"ShapeType_Rectangle"` → `"Rectangle"`, etc.
* If a value is *completely* missing, write `"N/A"` so downstream analysts notice.



Note

The slides/racks are scanned in alphabetical order. In the json file, in the "racks" heading there is "orderNumber" which is 1, 2, etc. based on the order the slide was scanned in (the first slide scanned is called 1, the second is called 2, etc.). And directly under "orderNumber" is "name". "name" gives the name we have given to the sample, eg Liver HF189 or whatever. In the "racks" tabs it would be important to link the order number with the name, as in list them in a row together so we know which slide was scanned when. 

