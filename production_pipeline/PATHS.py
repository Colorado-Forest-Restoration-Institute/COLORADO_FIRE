import os

# --- BASE DIRECTORIES ---
# Use absolute paths here.
ROOT_DIR = r'C:\Users\semue\Documents\GITHUB\Fire_Perimeters_Severity'
BOX_DIR = r'C:\Users\semue\Box\CFRI\Geodatabase\Colorado_Fire_Severity'
DRIVE_E = r'E:\CFRI'

# --- DERIVED PATHS ---
DATA_DIR = os.path.join(ROOT_DIR, 'data')
DWNLD_GDB = os.path.join(DATA_DIR, 'dwnld_perimeters.gdb')
SCRATCH_GDB = os.path.join(DATA_DIR, 'perimeter_update.gdb')
FINAL_GDB = os.path.join(DATA_DIR, 'final_perimeter_update.gdb')

# --- EXTERNAL ASSETS ---
STATES_LYR = os.path.join(DRIVE_E, r'BASE_LAYER_DATA\ADMINISTRATIVE_BOUNDARIES\US_States')
SEVERITY_BASE = os.path.join(DRIVE_E, r'Colorado_Fire_Severity\Fire_Severity_Data\1_Colorado_Severity_Data')
PERIMETERS = os.path.join(BOX_DIR,
                          r'Fire_Perimeters\Colorado_Fire_Perimeters_1984_2025.gdb\Colorado_Fire_Perimeters_1984_2025')


# --- SPECIFIC FEATURE CLASSES ---
INPUTS = {
    "mtbs": os.path.join(DWNLD_GDB, "mtbs_download"),
    "blm": os.path.join(DWNLD_GDB, "blm_download"),
    "ifpers": os.path.join(DWNLD_GDB, "ifpers_download"),
    "usfs": os.path.join(DWNLD_GDB, "usfs_download"),
    "wfigs_inter": os.path.join(DWNLD_GDB, "wfigs_interagency_download"),
    "wfigs_hist": os.path.join(DWNLD_GDB, "wfigs_historical_download"),
    "geomac": os.path.join(DWNLD_GDB, "geomac_download")
}

# --- FINAL OUTPUTS ---
PROVENANCE_TABLE = os.path.join(FINAL_GDB, "Fire_Perimeter_Provenance")
FINAL_PERIMETERS = os.path.join(FINAL_GDB, "fire_perimeters_update")
