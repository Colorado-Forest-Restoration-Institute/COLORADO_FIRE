# Colorado Fire Perimeter Processing

This project contains a set of **ArcPy scripts** used to compile, clean, and update fire perimeter data for Colorado.  
The workflow supports both **regular updates** (e.g., new data releases) and **quality control** (e.g., duplicate handling, provenance tracking).  

---

## Workflow Overview

1. **Download Data (`1_data_attribute_mapping.py`)**
   NOT FUNCTIONING AT THIS TIME -- ISSUES WITH DATA SOURCES -- DO NOT USE
   - Pulls source perimeter datasets (MTBS, NIFC, FACTS, BLM, etc.)  
   - May include normalization (field names, projections).  

2. **Duplicate Check (`2_tag_duplicates.py`)**  
   - Identifies overlapping/duplicate perimeters from different sources.  
   - Flags true duplicates and assigns a `priority` ranking to sources.  
   - Creates `duplication_check_output` in `perimeter_update.gdb`.  

3. **Finalize Update (`3_finalize_perimeters.py`)**  
   - For each duplicate group, selects the “best” record by priority.  
   - Merges attributes and dissolves geometry.  
   - Constructs consistent **Fire IDs** (MTBS-style) if missing.  
   - Standardizes names, labels, and units.  
   - Cleans fields, calculates acres, and writes to the final geodatabase.

Post Google Earch Engine processing (Parks et al. 2018)

4. **Classify Severity (`4_severity_organize.py`)**  
   - Extract Fire ID from filename (MTBS convention).
   - Lookup and sanitize Fire Name from MTBS perimeters.
   - Project raster to NAD83 UTM Zone 13N.
   - Reclassify into Unburned (1), Low (2), Moderate (3), and High (4) severity.
   - Clip both raw and classified rasters to the fire's boundary.
   - Organize output into structured subdirectories.   

---

## Project Structure

```
Fire_Perimeters/
│
├── SCRIPTS/ 
│	├── 1_data_attribute_mapping.py
│	├── 2_tag_duplicates.py
│	├── 3_finalize_perimeters.py
│	├── 4_severity_organize.py
├── README.md   
├── data/     ← working geodatabase folder
│	├── dwnld_perimeters.gdb
│	├── final_perimeter_update.gdb
│	   ├── fire_perimeters_update
│	├── perimeter_update.gdb
```

---

## Requirements

- ArcGIS Pro (with arcpy)  
- Python 3.x (as installed with ArcGIS Pro)  
- pandas, numpy, re  

---

## Usage

1. Run scripts in order:  
   ```
   python 01_download_data.py
   python 02_duplicate_check.py
   python 03_finalize_update.py
   ```
2. Final output will be written to:  
   ```
   final_perimeter_update.gdb/fire_perimeters_update
   ```
3. Intermediate Step: Requires processing in Google Earth Engine
   
4. Run script: python 04_severity_organize.py
   
5. Final rasters will be written to:
    ```
├── 1_Colorado_Severity_Data/ 
│	├── Classified/
│	├── Classified_Perimeter/
│	├── Unclassified/
│	├── Unclassified_Perimeter/
   ```
---

## Notes

- This repository is designed for repeatable updates as new fire perimeter data becomes available.  
- Future enhancements will contain information on processing fire severity.
