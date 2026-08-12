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
from datetime import date
from PATHS import SEVERITY_BASE, PERIMETERS

arcpy.env.overwriteOutput = True
arcpy.env.qualifiedFieldNames = False
arcpy.CheckOutExtension('spatial')

# Data Dictionaries
SEV_LOOKUP = {
    "dNBR": [53, 133],          # Low/Unburned < 53  | Mod >= 53  | High >= 133
    "dNBR_offset": [45, 125],   # Low/Unburned < 45  | Mod >= 45  | High >= 125
    "RBR": [47, 117],           # Low/Unburned < 47  | Mod >= 47  | High >= 117
    "RBR_offset": [40, 110],    # Low/Unburned < 40  | Mod >= 40  | High >= 110
    "RdNBR": [154, 376],        # Low/Unburned < 154 | Mod >= 154 | High >= 376
    "RdNBR_offset": [134, 356]  # Low/Unburned < 134 | Mod >= 134 | High >= 356
}

GEE_SUFFIX_MAP = {
    "dNBR": "dnbr",
    "dNBR_offset": "dnbr_w_offset",
    "RBR": "rbr",
    "RBR_offset": "rbr_w_offset",
    "RdNBR": "rdnbr",
    "RdNBR_offset": "rdnbr_w_offset"
}


def get_clean_name(raster_name, perimeter_layer):
    """
    Extracts ID from filename, looks up name in perimeters,
    and returns a sanitized version of both.
    """
    arcpy.management.SelectLayerByAttribute(perimeter_layer, "CLEAR_SELECTION")

    fire_id = raster_name[:21]
    field_name = "Fire_ID"
    query = f"{arcpy.AddFieldDelimiters(perimeter_layer, field_name)} = '{fire_id}'"
    clean_name = "UnknownFire"
    year = "0000"

    with arcpy.da.SearchCursor(perimeter_layer, ['Fire_Name', "Year"], where_clause=query) as cursor:
        for row in cursor:
            if row[0]:
                clean_name = re.sub(r'\W+', '', row[0]).lower()
            if row[1]:
                year = str(row[1])
            break

    return fire_id, clean_name, year


def classify_raster(in_raster, sev_type):
    """Applies reclassification based on the THRESHOLDS dictionary."""
    min_val = float(arcpy.GetRasterProperties_management(in_raster, "MINIMUM").getOutput(0))
    max_val = float(arcpy.GetRasterProperties_management(in_raster, "MAXIMUM").getOutput(0))

    limits = SEV_LOOKUP.get(sev_type)
    if not limits:
        arcpy.AddWarning(f"Severity type {sev_type} not found in SEV_LOOKUP.")
        return None

    l_max, m_max = limits

    # Format: [Start, End, NewValue]
    remap_list = []
    # Unburned/Low
    if min_val < l_max:
        remap_list.append([min_val - 1, l_max, 1])
    # Moderate
    if max_val > l_max and min_val < m_max:
        remap_list.append([l_max, m_max, 2])
    # High
    if max_val > m_max:
        start_high = m_max if min_val < m_max else min_val - 1
        remap_list.append([start_high, max_val + 1, 3])

    if not remap_list:
        arcpy.AddWarning(f"No valid reclassification ranges found for {sev_type} - (Min: {min_val}, Max: {max_val})")

    return Reclassify(in_raster, "VALUE", RemapRange(remap_list), "NODATA")


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
        proj_obj = Raster(proj_raster)
        classified_raster = classify_raster(proj_obj, sev_type)

        # 4. Define outpaths
        folders = {
            "unclass_ext": os.path.join(classification_dir, "Unclassified", sev_type),
            "unclass_clip": os.path.join(classification_dir, "Unclassified_Perimeter", sev_type),
            "class_ext": os.path.join(classification_dir, "Classified", sev_type),
            "class_clip": os.path.join(classification_dir, "Classified_Perimeter", sev_type)
        }

        for folder_path in folders.values():
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

        # Save Outputs
        query = f"Fire_ID = '{fire_id}'"
        arcpy.SelectLayerByAttribute_management(perimeter_lyr, "NEW_SELECTION", query)

        arcpy.management.CopyRaster(proj_obj, os.path.join(folders["unclass_ext"], out_base_name))
        classified_raster.save(os.path.join(folders["class_ext"], out_base_name))

        # Save Clips to Perimeter
        arcpy.management.Clip(
            proj_obj, "#", os.path.join(folders["unclass_clip"], out_base_name),
            perimeter_lyr, "#", "ClippingGeometry", "NO_MAINTAIN_EXTENT"
        )

        arcpy.management.Clip(
            classified_raster, "#", os.path.join(folders["class_clip"], out_base_name),
            perimeter_lyr, "#", "ClippingGeometry", "NO_MAINTAIN_EXTENT"
        )

        # 6. Cleanup Memory
        arcpy.management.Delete(proj_raster)
        del classified_raster
        del proj_obj

        print(f"Successfully processed {clean_name}")
        return None

    except Exception as e:
        error_msg = str(e)
        print(f"Failed:  {raster_name} | Reason: {error_msg}")
        return error_msg


# --- Start Processing Rasters ---
if arcpy.Exists("fire_perim_lyr"): arcpy.management.Delete("fire_perim_lyr")
fire_perim_lyr = arcpy.MakeFeatureLayer_management(PERIMETERS, "fire_perim_lyr")

failed_rasters = []

for sev in SEV_LOOKUP.keys():
    print(f"--- Starting Severity Group: {sev} ---")

    # Set current workspace to the unclassified data folder
    data_dir = os.path.join(SEVERITY_BASE, "raw_data")
    arcpy.env.workspace = data_dir

    gee_suffix = GEE_SUFFIX_MAP.get(sev)
    sev_rasters = arcpy.ListRasters(f"*_{gee_suffix}", "TIF")
    print(f"Found {len(sev_rasters) if sev_rasters else 0} rasters matching '*_{gee_suffix}.tif'")

    if sev_rasters:
        for raster in sev_rasters:
            result = process_fire(raster, sev, fire_perim_lyr, SEVERITY_BASE)

            if result:
                failed_rasters.append({
                    "Raster": raster,
                    "Type": sev,
                    "Reason": result
                })

# --- FINAL SUMMARY REPORT ---
print("\n" + "="*30)
print("PROCESSING SUMMARY")
print("="*30)

if failed_rasters:
    print(f"Total Failed: {len(failed_rasters)}")
    for item in failed_rasters:
        print(f"- {item['Raster']} ({item['Type']}): {item['Reason']}")

    file_date = date.today().strftime("%Y%m%d")
    log_file = os.path.join(SEVERITY_BASE, f"processing_errors_{file_date}.txt")

    with open(log_file, 'w') as f:
        f.write("Raster_Name, Severity_Type, Error_Reason\n")
        for item in failed_rasters:
            f.write(f"{item['Raster']}, {item['Type']}, {item['Reason']}\n")
    print(f"\nError log saved to: {log_file}")
else:
    print("All rasters processed successfully!")
