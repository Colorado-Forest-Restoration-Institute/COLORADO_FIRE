import os

# ==============================================================================
# --- BASE DIRECTORIES ---
# ==============================================================================
ROOT_DIR = r'C:\Users\semue\Documents\PROJECTS\COLORADO_FIRE'
BOX_DIR = r'C:\Users\semue\Box\CFRI\Geodatabase\Colorado_Fire'
DATA_REPO = r'C:\Users\semue\Documents\PROJECTS\DATA_REPOSITORY'

# ==============================================================================
# --- DERIVED PATHS ---
# ==============================================================================
DATA_DIR = os.path.join(ROOT_DIR, '2_data')
DATA_PERIMETER = os.path.join(DATA_DIR, 'fire_perimeter')
DATA_SEVERITY = os.path.join(DATA_DIR, 'fire_severity')
DATA_CBI = os.path.join(DATA_DIR, 'cbi')

# ==============================================================================
# --- THRESHOLD CALIBRATION WORKFLOW ---
# ==============================================================================
# Paths for your CBI validation plots and calibration statistics scripts
CBI_PLOTS_CSV = os.path.join(DATA_CBI, 'cbi_plot_data.csv')
THRESH_OUTPUTS = os.path.join(DATA_CBI, 'CALIBRATION_RESULTS')

# ==============================================================================
# --- PERIMETER WORKFLOW ---
# ==============================================================================
DWNLD_GDB = os.path.join(DATA_PERIMETER, 'dwnld_perimeters.gdb')
SCRATCH_GDB = os.path.join(DATA_PERIMETER, 'perimeter_update.gdb')
FINAL_GDB = os.path.join(DATA_PERIMETER, 'final_perimeter_update.gdb')

# Specific Feature Classes for downloading & merging agency datasets
INPUTS = {
    "mtbs": os.path.join(DWNLD_GDB, "mtbs_download"),
    "blm": os.path.join(DWNLD_GDB, "blm_download"),
    "ifpers": os.path.join(DWNLD_GDB, "ifpers_download"),
    "usfs": os.path.join(DWNLD_GDB, "usfs_download"),
    "wfigs_inter": os.path.join(DWNLD_GDB, "wfigs_interagency_download"),
    "wfigs_hist": os.path.join(DWNLD_GDB, "wfigs_historical_download"),
    "geomac": os.path.join(DWNLD_GDB, "geomac_download")
}

PROVENANCE_TABLE = os.path.join(FINAL_GDB, "Fire_Perimeter_Provenance")
FINAL_PERIMETERS = os.path.join(FINAL_GDB, "fire_perimeters_update")

# ==============================================================================
# --- SEVERITY WORKFLOW ---
# ==============================================================================
# Working workspace where raw GEE rasters live locally
SEVERITY_DIR = os.path.join(DATA_SEVERITY, '1_Colorado_Severity_Data')

# Local target folders for your production classification script outputs
UNCLASSIFIED_DIR_LOCAL = os.path.join(DATA_SEVERITY, 'Unclassified')
CLASSIFIED_DIR_LOCAL = os.path.join(DATA_SEVERITY, 'Classified')
CLASSIFIED_CLIP_LOCAL = os.path.join(DATA_SEVERITY, 'Classified_Perimeter')
UNCLASSIFIED_CLIP_LOCAL = os.path.join(DATA_SEVERITY, 'Unclassified_Perimeter')

# ==============================================================================
# --- EXTERNAL / TEAM ASSETS (BOX & REPO) ---
# ==============================================================================
STATES_LYR = os.path.join(DATA_REPO, r'BASE_LAYER_DATA\ADMINISTRATIVE_BOUNDARIES\US_States')

# Master collaborative perimeters file that lives on Box
PERIMETERS = os.path.join(BOX_DIR, r'Fire_Perimeters\Colorado_Fire_Perimeters_1984_2025.gdb\Colorado_Fire_Perimeters_1984_2025')

# The final, shared public deployment location on Box for coworkers to scrape
BOX_SEVERITY_DEPLOYMENT = os.path.join(BOX_DIR, 'Ready_To_Use_Severity_Products')
