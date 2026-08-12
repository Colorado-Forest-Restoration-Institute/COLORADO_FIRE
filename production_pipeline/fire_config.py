from PATHS import INPUTS

dt_start = 1984  # START DATE for filter (inclusive)
dt_end = 2026  # END DATE for filter (exclusive)

state_abbr = "NV"  # Perimeter intersect state

# Dictionary of final fields
FINAL_FIELDS = {"n_Fire_ID": "TEXT",
                "n_Fire_Name": "TEXT",
                "n_Fire_Label": "TEXT",
                "n_Year": "LONG",
                "n_StartMonth": "SHORT",
                "n_StartDay":"SHORT",
                "n_GIS_Acres": "FLOAT",
                "n_Fire_Type": "TEXT",
                "n_Agency": "TEXT",
                "n_Source": "TEXT",
                "n_SourceID": "TEXT",
                "n_Priority": "SHORT"
                }

# Dataset mappings

# MTBS
mtbs_mapping = {
    "n_Fire_ID": lambda row: row['FIRE_ID'],
    "n_Fire_Name": lambda row: 'Unknown' if row['FIRE_NAME'] == 'UNNAMED' else row['FIRE_NAME'],
    "n_Fire_Label": lambda row: row['FIRE_NAME'].title() if row['FIRE_NAME'] else None,
    "n_Year": lambda row: row['YEAR'],
    "n_StartMonth": lambda row: row['STARTMONTH'],
    "n_StartDay": lambda row: row['STARTDAY'],
    "n_GIS_Acres": lambda row: None,
    "n_Fire_Type": lambda row: row['FIRE_TYPE'],
    "n_Agency": lambda row: None,
    "n_Source": lambda row: 'MTBS',
    "n_SourceID": lambda row: row['FIRE_ID'],
    "n_Priority": lambda row: '1'
    }

# WFIGS interagency
wfigs_interagency_mapping = {
    "n_Fire_ID": lambda row: None,
    "n_Fire_Name": lambda row: row['poly_IncidentName'],
    "n_Fire_Label": lambda row: row['poly_IncidentName'].title() if row['poly_IncidentName'] else None,
    "n_Year": lambda row: row['attr_FireDiscoveryDateTime'].year if row['attr_FireDiscoveryDateTime'] else None,
    "n_StartMonth": lambda row: row['attr_FireDiscoveryDateTime'].month if row['attr_FireDiscoveryDateTime'] else None,
    "n_StartDay": lambda row: row['attr_FireDiscoveryDateTime'].day if row['attr_FireDiscoveryDateTime'] else None,
    "n_GIS_Acres": lambda row: None,
    "n_Fire_Type": lambda row: 'Prescribed Fire' if row['attr_IncidentTypeCategory'] == 'RX' else 'Wildfire',
    "n_Agency": lambda row: row['attr_POOProtectingAgency'],
    "n_Source": lambda row: 'WFIGS Interagency',
    "n_SourceID": lambda row: row['attr_UniqueFireIdentifier'],
    "n_Priority": lambda row: '2'
    }


# WFIGS historical
wfigs_historical_mapping = {
    "n_Fire_ID": lambda row: None,
    "n_Fire_Name": lambda row: row['INCIDENT'],
    "n_Fire_Label": lambda row: row['INCIDENT'].title() if row['INCIDENT'] else None,
    "n_Year": lambda row: row['FIRE_YEAR'],
    "n_StartMonth": lambda row: None,
    "n_StartDay": lambda row: None,
    "n_GIS_Acres": lambda row: None,
    "n_Fire_Type": lambda row: 'Wildfire' if row['FEATURE_CA'] and row['FEATURE_CA'].startswith('Wildfire') else 'Prescribed Fire',
    "n_Agency": lambda row: row['AGENCY'],
    "n_Source": lambda row: 'WFIGS Historical',
    "n_SourceID": lambda row: row['UNQE_FIRE_ID'] if row['UNQE_FIRE_ID'] else None,
    "n_Priority": lambda row: '3'
    }

# GeoMAC
geomac_mapping = {
    "n_Fire_ID": lambda row: None,
    "n_Fire_Name": lambda row: row['incidentname'],
    "n_Fire_Label": lambda row: row['incidentname'].title() if row['incidentname'] else None,
    "n_Year": lambda row: row['fireyear'],
    "n_StartMonth": lambda row: row['perimeterdatetime'].month if row['perimeterdatetime'] else None,
    "n_StartDay": lambda row: row['perimeterdatetime'].day if row['perimeterdatetime'] else None,
    "n_GIS_Acres": lambda row: None,
    "n_Fire_Type": lambda row: 'Wildfire',
    "n_Agency": lambda row: row['agency'],
    "n_Source": lambda row: 'Geomac',
    "n_SourceID": lambda row: row['uniquefireidentifier'] if row['uniquefireidentifier'] else None,
    "n_Priority": lambda row: "4"
    }

# BLM Colorado
blm_mapping = {
    "n_Fire_ID": lambda row: None,
    "n_Fire_Name": lambda row: row['TRTMNT_NM'],
    "n_Fire_Label": lambda row: row['TRTMNT_NM'].title() if row['TRTMNT_NM'] else None,
    "n_Year": lambda row: row['TRTMNT_START_DT'].year if row['TRTMNT_START_DT'] else None,
    "n_StartMonth": lambda row: row['TRTMNT_START_DT'].month if row['TRTMNT_START_DT'] else None,
    "n_StartDay": lambda row: row['TRTMNT_START_DT'].day if row['TRTMNT_START_DT'] else None,
    "n_GIS_Acres": lambda row: None,
    "n_Fire_Type": lambda row: 'Prescribed Fire',
    "n_Agency": lambda row: 'BLM',
    "n_Source": lambda row: 'BLM VTRT',
    "n_SourceID": lambda row: row['UNIQUE_ID'] if row['UNIQUE_ID'] else None,
    "n_Priority": lambda row: '7'
    }

# IFPERS
ifpers_mapping = {
    "n_Fire_ID": lambda row: None,
    "n_Fire_Name": lambda row: row['Name'],
    "n_Fire_Label": lambda row: row['Name'].title() if row['Name'] else None,
    "n_Year": lambda row: row['InitiationDate'].year if row['InitiationDate'] else None,
    "n_StartMonth": lambda row: row['InitiationDate'].month if row['InitiationDate'] else None,
    "n_StartDay": lambda row: row['InitiationDate'].day if row['InitiationDate'] else None,
    "n_GIS_Acres": lambda row: None,
    "n_Fire_Type": lambda row: 'Prescribed Fire',
    "n_Agency": lambda row: row['Agency'],
    "n_Source": lambda row: 'IFPERS Open Data',
    "n_SourceID": lambda row: row['ID'] if row['ID'] else None,
    "n_Priority": lambda row: '5'
    }

# USFS FACTS Common Attributtes
usfs_mapping = {
    "n_Fire_ID": lambda row: None,
    "n_Fire_Name": lambda row: row['NAME'],
    "n_Fire_Label": lambda row: row['NAME'].title() if row['NAME'] else None,
    "n_Year": lambda row: row['DATE_COMPLETED'].year if row['DATE_COMPLETED'] else None,
    "n_StartMonth": lambda row: row['DATE_COMPLETED'].month if row['DATE_COMPLETED'] else None,
    "n_StartDay": lambda row: row['DATE_COMPLETED'].day if row['DATE_COMPLETED'] else None,
    "n_GIS_Acres": lambda row: None,
    "n_Fire_Type": lambda row: "Prescribed Fire",
    "n_Agency": lambda row: 'USFS',
    "n_Source": lambda row: 'USFS FACTS',
    "n_SourceID": lambda row: row['EVENT_CN'],
    "n_Priority": lambda row: "6"
    }

# Data filters
blm_filter = (
    "TRTMNT_TYPE_CD = 3 AND "
    "UPPER(TRTMNT_NM) NOT LIKE '%PILE%' AND "
    "UPPER(TRTMNT_COMMENTS) NOT LIKE '%PILE%' AND "
    "UPPER(TRTMNT_NM) NOT LIKE '%PILING%' AND "
    "UPPER(TRTMNT_COMMENTS) NOT LIKE '%PILING%' AND "
    "UPPER(TRTMNT_NM) NOT LIKE '%WILDFIRE%' AND "
    "UPPER(TRTMNT_COMMENTS) NOT LIKE '%WILDFIRE%' AND "
    "UPPER(TRTMNT_NM) NOT LIKE '%FIRE USE%' AND "
    "UPPER(TRTMNT_COMMENTS) NOT LIKE '%FIRE USE%'"
)

ifpers_filter = (
    "Class = 'Actual Treatment' AND "
    "Type = 'Broadcast' OR "
    "Type = 'Underburn' "
                 )

usfs_filter = (
    "ACTIVITY = 'Broadcast Burning - Covers a majority of the unit' OR "
    "ACTIVITY = 'Control of Understory Vegetation- Burning' OR "
    "ACTIVITY = 'Site Preparation for Natural Regeneration - Burning' OR "
    "ACTIVITY = 'Site Preparation for Planting - Burning' OR "
    "ACTIVITY = 'Underburn - Low Intensity (Majority of Unit)' "
)

SOURCE_REGISTRY = [
    {"name": "mtbs",
     "input": INPUTS["mtbs"],
     "mapping": mtbs_mapping,
     "where_clause": None
     },
    {"name": "wfigs_interagency",
     "input": INPUTS["wfigs_inter"],
     "mapping": wfigs_interagency_mapping,
     "where_clause": None
     },
    {"name": "wfigs_historical",
     "input": INPUTS["wfigs_hist"],
     "mapping": wfigs_historical_mapping,
     "where_clause": None
     },
    {"name": "geomac",
     "input": INPUTS["geomac"],
     "mapping": geomac_mapping,
     "where_clause": None
     },
    {"name": "blm",
     "input": INPUTS["blm"],
     "mapping": blm_mapping,
     "where_clause": blm_filter
     },
    {"name": "ifpers",
     "input": INPUTS["ifpers"],
     "mapping": ifpers_mapping,
     "where_clause": ifpers_filter
     },
    {"name": "usfs",
     "input": INPUTS["usfs"],
     "mapping": usfs_mapping,
     "where_clause": usfs_filter
     }
]
