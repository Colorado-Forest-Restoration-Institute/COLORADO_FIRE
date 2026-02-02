"""
Purpose:
--------
Processes Google Earth Engine severity rasters (Parks et al. 2018) by projecting,
reclassifying into three severity classes, and clipping to specific fire perimeters.

Workflow:
---------
1. Extract Fire ID from filename (MTBS convention).
2. Lookup and sanitize Fire Name from MTBS perimeters.
3. Project raster to NAD83 UTM Zone 13N.
4. Reclassify into Unburned (1), Low (2), Moderate (3), and High (4) severity.
5. Clip both raw and classified rasters to the fire's boundary.
6. Organize output into structured subdirectories.

Input Requirements:
-------------------
- Raster Naming: Must start with 21-character MTBS ID (e.g., 'CO4020910894720090807_dnbr.tif').
- Perimeters: A GDB feature class with 'Fire_ID' (matches raster prefix) and 'Fire_Name'.

Severity Thresholds (Low_Max, Mod_Max):
---------------------------------------
[Class 1: Unburned <= Limit1] | [Class 2: Low <= Limit1] | [Class 3: Mod <= Limit2] | [Class 4: High > Limit2]

- dNBR:          23, 96, 150    |  - dNBR Offset:   16, 89, 144
- RBR:           20, 83, 131    |  - RBR Offset:    14, 78, 126
- RdNBR:         65, 262, 410   |  - RdNBR Offset:  48, 256, 394

Outputs:
--------
Structured by Severity Type (e.g., Classified_Perimeter/dNBR/):
1. Classified Extent: Full projected & reclassified raster.
2. Classified Clip:   Severity classes clipped to fire perimeter.
3. Unclassified Clip: Raw index values clipped to fire perimeter.
"""

import arcpy
import os
import re
from arcpy.sa import *

arcpy.env.overwriteOutput = True
arcpy.env.qualifiedFieldNames = False
arcpy.CheckOutExtension('spatial')

# --- Configurable Base Directories ---
base_dir = r'E:\CFRI\Colorado_Fire_Severity\Fire_Severity_Data\1_Colorado_Severity_Data'  # Location of raw_data data folder
perimeters = r'C:\Users\semue\Box\CFRI\Geodatabase\Colorado_Fire_Severity\Fire_Perimeters\Colorado_Fire_Perimeters_1984_2024.gdb\Colorado_Fire_Perimeters_1984_2024'

# Data Dictionaries
SEV_TYPES = ["dNBR", "dNBR_offset", "RBR", "RBR_offset", "RdNBR", "RdNBR_offset"]
#SEV_TYPES = ["dNBR"]  # When running very large datasets, it is recommended to run severity subsets to avoid crashout #

SEV_LOOKUP = {
    "dNBR": [23, 96, 150],
    "dNBR_offset": [16, 89, 144],
    "RBR": [20, 83, 131],
    "RBR_offset": [14, 78, 126],
    "RdNBR": [65, 262, 410],
    "RdNBR_offset": [48, 246, 394]
}


def get_clean_name(raster_name, perimeter_layer):
    """
    Extracts ID from filename, looks up name in perimeters,
    and returns a sanitized version of both.
    """
    fire_id = raster_name[:21]
    query = f"{arcpy.AddFieldDelimiters(perimeter_layer, 'Fire_ID')} = '{fire_id}'"
    clean_name = "UnknownFire"
    year = "0000"

    with arcpy.da.SearchCursor(perimeter_layer, ['Fire_Name', "Year"], where_clause=query) as cursor:
        for row in cursor:
            raw_name = row[0]
            year = str(row[1])
            clean_name = re.sub(r'\W+', '', raw_name).lower()

    return fire_id, clean_name, year


def classify_raster(in_raster, sev_type):
    """Applies reclassification based on the THRESHOLDS dictionary."""
    min_val = float(arcpy.GetRasterProperties_management(in_raster, "MINIMUM").getOutput(0))
    max_val = float(arcpy.GetRasterProperties_management(in_raster, "MAXIMUM").getOutput(0))

    limits = SEV_LOOKUP.get(sev_type)
    if not limits: return None

    ub_max, l_max, m_max = limits

    # Format: [Start, End, NewValue]
    remap = RemapRange([
        [min_val - 1, ub_max, 1],    # Unburned
        [ub_max + 1, l_max, 2],      # Low
        [l_max + 1, m_max, 3],       # Moderate
        [m_max + 1, max_val + 1, 4]  # High
    ])

    return Reclassify(in_raster, "VALUE", remap, "NODATA")


def process_fire(raster_name, sev_type, perimeter_lyr, classification_dir):
    """
    Handles the full workflow for a single raster:
    Project -> Rename -> Classify -> Clip -> Save
    """
    try:
        # 1. Get Name
        fire_id, clean_name, year = get_clean_name(raster_name, perimeter_lyr)
        out_base_name = f"{clean_name}_{year}_{fire_id}_{sev_type}.tif"
        print(f"Processing: {out_base_name}")

        # 2. Project
        sr_utm13 = arcpy.SpatialReference(26913)
        proj_raster = os.path.join("memory", "proj_temp")
        arcpy.ProjectRaster_management(raster_name, proj_raster, sr_utm13, "BILINEAR", "30 30")

        # 3. Reclassify
        classified_raster = classify_raster(proj_raster, sev_type)

        # 4. Define outpaths
        folders = {
            "unclass_ext": os.path.join(base_dir, "Unclassified", sev_type),
            "unclass_clip": os.path.join(base_dir, "Unclassified_Perimeter", sev_type),
            "class_ext": os.path.join(base_dir, "Classified", sev_type),
            "class_clip": os.path.join(base_dir, "Classified_Perimeter", sev_type)
        }

        for folder_path in folders.values():
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

        # Save Outputs
        query = f"FIRE_ID = '{fire_id}'"
        arcpy.SelectLayerByAttribute_management(perimeter_lyr, "NEW_SELECTION", query)

        arcpy.management.CopyRaster(proj_raster, os.path.join(folders["unclass_ext"], out_base_name))
        classified_raster.save(os.path.join(folders["class_ext"], out_base_name))

        # Save Clips to Perimeter
        arcpy.management.Clip(
            proj_raster, "#", os.path.join(folders["unclass_clip"], out_base_name),
            perimeter_lyr, "#", "ClippingGeometry", "NO_MAINTAIN_EXTENT"
        )

        arcpy.management.Clip(
            classified_raster, "#", os.path.join(folders["class_clip"], out_base_name),
            perimeter_lyr, "#", "ClippingGeometry", "NO_MAINTAIN_EXTENT"
        )

        # 6. Cleanup Memory
        arcpy.management.Delete(proj_raster)
        arcpy.management.Delete(classified_raster)

        print(f"Successfully processed {clean_name}")

    except Exception as e:
        print(f"Failed to process {raster_name}: {e}")


# --- Start Processing Rasters ---
fire_perim_lyr = arcpy.MakeFeatureLayer_management(perimeters, "fire_perim_lyr")

for sev in SEV_TYPES:
    print(f"--- Starting Severity Group: {sev} ---")

    # Set current workspace to the unclassified data folder
    data_dir = os.path.join(base_dir, "raw_data", sev)
    arcpy.env.workspace = data_dir

    sev_rasters = arcpy.ListRasters("*.tif")
    for raster in sev_rasters:
        process_fire(raster, sev, fire_perim_lyr, base_dir)

print("Task Completed!")
