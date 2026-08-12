"""
Colorado Fire Perimeter Integration and Attribute Mapping Script
------------------------------------------

This script prepares and standardizes wildfire and prescribed fire perimeter datasets
from multiple sources into a single geodatabase for further analysis. It applies a
consistent field schema, filters features by year, and merges outputs into a unified
feature class. Sources currently included:

    - MTBS
    - WFIGS (Interagency & Historical)
    - GeoMAC
    - BLM Colorado
    - DOI IFPERS
    - USFS FACTS

⚠ Pre-processing required:
At this stage, the script assumes that perimeter data from the various sources has
already been downloaded, clipped to Colorado, and stored in a geodatabase called:

    dwnld_perimeters.gdb

This geodatabase should reside inside the UPDATE folder defined in `base_dir`.
Each source must be placed in `dwnld_perimeters.gdb` under the expected
feature class names (e.g., mtbs_download, wfigs_interagency_download, etc.).

Example directory structure:

    E:\CFRI\Colorado_Fire_Severity\Fire_Perimeters\
        ├── UPDATE\
        │     ├── dwnld_perimeters.gdb\
        │     │      ├── mtbs_download
        │     │      ├── wfigs_interagency_download
        │     │      ├── wfigs_historical_download
        │     │      ├── geomac_download
        │     │      ├── blm_download
        │     │      ├── ifpers_download
        │     │      └── usfs_download
        │     └── perimeter_update.gdb   (scratch workspace, created by script)

The script then:
    - Copies and standardizes attributes across datasets
    - Adds missing fields to match a final schema
    - Applies mapping rules to harmonize naming, dates, and identifiers
    - Filters perimeters to a given year range (default: 1984–2024)
    - Selects prescribed fire treatments for BLM and USFS
    - Merges all outputs into a single feature class:
        raw_Colorado_Fire_Perimeters_duplicates
    - Repairs geometry and removes extraneous fields

Future enhancements will include automating the pre-processing steps so that
downloaded datasets can be ingested directly.
"""

import arcpy
import os
from collections import Counter
from PATHS import SCRATCH_GDB, STATES_LYR
from fire_config import SOURCE_REGISTRY, FINAL_FIELDS, state_abbr, dt_start, dt_end

arcpy.env.workspace = SCRATCH_GDB
arcpy.env.overwriteOutput = True

# --- Temporary Outputs ---
tmp_mapping = os.path.join(SCRATCH_GDB, "tmp_mapping")

# --- Final Output for Combined Perimeters ---
combined_perimeters = os.path.join(SCRATCH_GDB, "raw_Colorado_Fire_Perimeters_duplicates")


def add_new_fields(fc, final_field_list):
    """ Add final gdb fields to perimeter feature classes """
    existing_fields = [f.name for f in arcpy.ListFields(fc)]
    for field_name, field_type in final_field_list.items():
        if field_name not in existing_fields:
            arcpy.AddField_management(fc, field_name, field_type)


def apply_mapping(fc, mapping, final_field_list):
    """ Update new fields in the feature class using the provided mapping """
    all_fields = list(set(mapping.keys()).union(fc_fields(fc)))

    with arcpy.da.UpdateCursor(fc, all_fields) as cursor:
        for row in cursor:
            row_dict = dict(zip(all_fields, row))
            updated_row = list(row)

            for field_name in final_field_list.keys():
                map_func = mapping.get(field_name)
                if map_func:
                    try:
                        value = map_func(row_dict)
                        updated_row[all_fields.index(field_name)] = value
                    except Exception as e:
                        print(f"Error processing field {field_name}: {e}")

            cursor.updateRow(updated_row)


def filter_perimeters(fc, state_layer, state_abbr, start_year, end_year, final_output):
    state_query = f"STATE_ABBR = '{state_abbr}'"
    arcpy.MakeFeatureLayer_management(state_layer, "temp_state_bndy", state_query)

    year_query = f"n_Year >= {start_year} AND n_Year < {end_year}"
    arcpy.MakeFeatureLayer_management(fc, "temp_fires_perims", year_query)
    print(f"Selecting fires for {state_abbr} between {start_year} and {end_year}")

    arcpy.management.SelectLayerByLocation(
        in_layer="temp_fires_perims",
        overlap_type="INTERSECT",
        select_features="temp_state_bndy",
        selection_type="NEW_SELECTION"
    )

    count = int(arcpy.management.GetCount("temp_fires_perims")[0])
    print(f"Filter result: {count} fires found for {final_output}")

    arcpy.CopyFeatures_management("temp_fires_perims", final_output)

    arcpy.Delete_management("temp_fires_perims")
    arcpy.Delete_management("temp_state_bndy")


def fc_fields(fc):
    """ Get a list of all field names in the feature class """
    return [f.name for f in arcpy.ListFields(fc)]


def process_fire_layer(input_fc, working_fc, mapping, final_field_list, state_layer, state_abbr, final_output,
                           start_year, end_year):
    """ Full process: add fields, apply mapping, and save to output"""
    print(f"Processing {input_fc}")
    arcpy.CopyFeatures_management(input_fc, working_fc)
    add_new_fields(working_fc, final_field_list)
    apply_mapping(working_fc, mapping, final_field_list)
    arcpy.management.RepairGeometry(working_fc)
    filter_perimeters(working_fc, state_layer, state_abbr, start_year, end_year, final_output)
    arcpy.Delete_management(working_fc)
    print(f"Saved output to {final_output}")


# --- Start Processing ---
for source in SOURCE_REGISTRY:
    input_data = source['input']

    # Check if source exists
    if not arcpy.Exists(input_data):
        print(f"{source} is not available")
        continue

    # Apply pre-filter (DOI/BLM/USFS) if exists
    if source['where_clause']:
        print(f"Applying pre-filter to {source['name']}...")
        temp_lyr = f"lyr_{source['name']}"
        arcpy.management.MakeFeatureLayer(source['input'], temp_lyr, source['where_clause'])
        input_data = temp_lyr

    out_path = os.path.join(SCRATCH_GDB, f"mapping_{source['name']}")

    # Check if input exists before processing
    process_fire_layer(
        input_data,
        tmp_mapping,
        source['mapping'],
        FINAL_FIELDS,
        STATES_LYR,
        state_abbr,
        out_path,
        dt_start,
        dt_end
    )

    # Clean up the temporary selection layer
    if source['where_clause']:
        arcpy.management.Delete(temp_lyr)

# Combine all perimeters
mapping_list = arcpy.ListFeatureClasses("mapping_*")
first_fc = os.path.join(SCRATCH_GDB, mapping_list[0])
arcpy.CreateFeatureclass_management(
    out_path=SCRATCH_GDB,
    out_name="raw_Colorado_Fire_Perimeters_duplicates",
    template=first_fc,
    spatial_reference=first_fc
)

# 3. Use Append with NO_TEST to force the data in
print(f"Appending {len(mapping_list)} layers into the final container...")
arcpy.Append_management(
    inputs=mapping_list,
    target=combined_perimeters,
    schema_type="NO_TEST"
)

perimeters_merge_path = combined_perimeters

# Repair geometry of final layer
arcpy.RepairGeometry_management(perimeters_merge_path)

# Delete extraneous fields
print("Deleting unnecessary fields")
perimeter_fields = set(FINAL_FIELDS.keys())
merge_fields = [f.name for f in arcpy.ListFields(perimeters_merge_path)]
for fld in merge_fields:
    if fld not in perimeter_fields and fld.lower() not in ['objectid', 'shape', 'shape_length', 'shape_area']:
        try:
            arcpy.DeleteField_management(perimeters_merge_path, fld)
        except:
            print(f"{fld} not deleted")


# Check how many records came from each source in the final merge
with arcpy.da.SearchCursor(combined_perimeters, ["n_Source"]) as cursor:
    print(Counter(row[0] for row in cursor))
