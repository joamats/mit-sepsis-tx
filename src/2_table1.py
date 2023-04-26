from tableone import TableOne
import pandas as pd

def table_one(cohort_number, hr_period, sf_period):

    data = pd.read_csv(f'data/MIMIC_coh_{cohort_number}.csv')

    # Encode race_white as being white vs. non-white
    data['race_white'] = data.race_group.apply(lambda x: "White" if x == "White" else "Racial-Ethnic Group")

    # Groupby Variable
    groupby = ['race_white']

    # Continuous Variables
    data['los_hosp_dead'] = data[data.mortality_in == 1].los_hospital
    data['los_hosp_surv'] = data[data.mortality_in == 0].los_hospital

    data['los_icu_dead'] = data[data.mortality_in == 1].los_icu
    data['los_icu_surv'] = data[data.mortality_in == 0].los_icu

    # Encode language as English proficiency or Limited English proficiency
    data['eng_prof'] = data['language'].apply(lambda x: "Limited" if x == '?' else "Proficient")

    # Create variable for receiving fluids, if fluid volume is not na
    data['fluids_overall'] = data['fluids_volume'].apply(lambda x: 1. if x > 0 else 0.)

    # Encode absolute durations and offsets into hours
    data['MV_time_abs'] = data['MV_time_abs'] * 24
    data['VP_time_abs'] = data['VP_time_abs'] * 24
    data['MV_init_offset_abs'] = data['MV_init_offset_abs'] * 24
    data['RRT_init_offset_abs'] = data['RRT_init_offset_abs'] * 24
    data['VP_init_offset_abs'] = data['VP_init_offset_abs'] * 24

    # Encode NA as 0, if missing means 0
    cols_na = ['major_surgery', 'insulin_yes', 'transfusion_yes', 'hypertension_present',
            'heart_failure_present', 'copd_present', 'asthma_present', 'cad_present',
            'ckd_stages', 'diabetes_types', 'connective_disease', 'pneumonia',
            'uti', 'biliary', 'skin']

    for c in cols_na:
        data[c] = data[c].fillna(0)

    # Encode diabetes and CKD 0 as "Absent"
    data['diabetes_types'] = data['diabetes_types'].apply(lambda x: "Absent" if x == 0 else x)
    data['ckd_stages'] = data['ckd_stages'].apply(lambda x: "Absent" if x == 0 else x)

    order = {
        #"race_group": ["White", "Black", "Hispanic", "Asian", "Other"],
        "gender": ["F", "M"],
        "eng_prof": ["Limited", "Proficient"],
        "insurance": ["Medicare", "Medicaid", "Other"],
        "adm_elective": [1, 0],
        "major_surgery": [1., 0.],
        "mortality_in": [1, 0],
        "mortality_90": [1, 0],
        "mech_vent_overall": [1, 0],
        "rrt_overall": [1, 0],
        "vasopressor_overall": [1, 0],
        "insulin_yes": [1., 0.],
        "transfusion_yes": [1., 0.],
        "fluids_overall": [1., 0.],
        "hypertension_present": [1., 0.],
        "heart_failure_present": [1., 0.],
        "copd_present": [1., 0.],
        "asthma_present": [1., 0.],
        "cad_present": [1., 0.],
        "connective_disease": [1., 0.],
        "pneumonia": [1., 0.],
        "uti": [1., 0.],
        "biliary": [1., 0.],
        "skin": [1., 0.],
    }

    limit = {"gender": 1,
            "adm_elective": 1,
            "major_surgery": 1,
            "mortality_in": 1,
            "mortality_90": 1,
            "eng_prof": 1,
            "mech_vent_overall": 1,
            "rrt_overall": 1,
            "vasopressor_overall": 1,
            "insulin_yes": 1,
            "transfusion_yes": 1,
            "fluids_overall": 1,
            "hypertension_present": 1,
            "heart_failure_present": 1,
            "copd_present": 1,
            "asthma_present": 1,
            "cad_present": 1,
            "connective_disease": 1,
            "pneumonia": 1,
            "uti": 1,
            "biliary": 1,
            "skin": 1,
            }


    categ = ['anchor_year_group', 'gender',
            'insurance', 'eng_prof',
            'adm_elective', 'major_surgery',
            'mortality_in', 'mortality_90',
            'mech_vent_overall', 'rrt_overall', 'vasopressor_overall',
            'insulin_yes', 'transfusion_yes', 'fluids_overall',
            'hypertension_present', 'heart_failure_present',
            'copd_present', 'asthma_present', 'cad_present',
            'ckd_stages', 'diabetes_types', 'connective_disease',
            'pneumonia', 'uti', 'biliary', 'skin'
            ]

    nonnorm = ['admission_age', 
               'los_icu_dead', 'los_icu_surv',
               'los_hosp_dead', 'los_hosp_surv',
               'charlson_comorbidity_index',
               'SOFA_admit', 'respiratory_admit', 'coagulation_admit',
               'liver_admit', 'cardiovascular_admit', 'cns_admit', 'renal_admit',
               f'sofa_max_{sf_period}',
               f'respiratory_max_{sf_period}',
               f'coagulation_max_{sf_period}',
               f'liver_max_{sf_period}',
               f'cardiovascular_max_{sf_period}',
               f'cns_max_{sf_period}',
               f'renal_max_{sf_period}',
               f'fluids_{hr_period}',
               'fluids_volume',
               'fluids_volume_norm_by_los_icu',
               f'FiO2_mean_{hr_period}',
               'MV_time_abs', 'MV_time_perc_of_stay',
               'MV_init_offset_abs',
               'RRT_init_offset_abs', 
               'VP_init_offset_abs', 
               'VP_time_abs', 'VP_time_perc_of_stay',
               f'resp_rate_mean_{hr_period}',
               f'mbp_mean_{hr_period}',
               f'temperature_mean_{hr_period}',
               f'spo2_mean_{hr_period}',
               f'heart_rate_mean_{hr_period}',
               f'po2_min_{hr_period}',
               f'pco2_max_{hr_period}',
               f'ph_min_{hr_period}',
               f'glucose_max_{hr_period}',
               f'sodium_min_{hr_period}',
               f'potassium_max_{hr_period}',
               f'cortisol_min_{hr_period}',
               f'hemoglobin_min_{hr_period}',
               f'fibrinogen_min_{hr_period}',
               f'inr_max_{hr_period}'
            ]  

    labls = {
        'anchor_age': 'Age',
        'anchor_year_group': 'Year of Admission',
        'admission_age': 'Age',
        'gender': 'Sex ',
        'mortality_in': "In-Hospital Mortality",
        'mortality_90': "90-Day Mortality",
        'eng_prof': "English Proficiency",
        'adm_elective': "Elective Admission",
        'major_surgery': "Major Surgery",
        'insurance': "Health Insurance",
        'race_group': "Race-Ethnicity Group",
        'mech_vent_overall': 'Mechanical Ventilation (whole stay)',
        'rrt_overall': "RRT (whole stay)",
        'vasopressor_overall': 'Vasopressors (whole stay)',
        'insulin_yes': 'Insulin Transfusion (whole stay)',
        'transfusion_yes': "Blood Transufusion (whole stay)",
        'fluids_overall': "Fluids Received (whole stay)",
        'hypertension_present': "Hypertension",
        'heart_failure_present': "Congestive Heart Failure",
        'copd_present': "COPD",
        'asthma_present': "Asthma",
        'cad_present': "Coronary Artery Disease",
        'ckd_stages': "CKD Stage",
        'diabetes_types': "Diabetes Type",
        'connective_disease': "Connective Tissue Disease",
        'pneumonia': "Pneumonia",
        'uti': "Urinary Tract Infection",
        'biliary': "Biliary Tract Infection",
        'skin': "Skin Infection",
        'los_icu_dead': "ICU LOS (days, if deceased)",
        'los_icu_surv': "ICU LOS (days, if survived)",
        'los_hosp_dead': "Hospital LOS (days, if deceased)",
        'los_hosp_surv': "Hospital LOS (days, if survived)",
        'charlson_comorbidity_index': "Charlson Comorbidity Index",
        'SOFA_admit': "SOFA Score (admission)",
        f'respiratory_admit': "SOFA: Respiratory (admission)",
        f'coagulation_admit': "SOFA: Coagulation (admission)",
        f'liver_admit': "SOFA: Liver (admission)",
        f'cardiovascular_admit': "SOFA: Cardiovascular (admission)",
        f'cns_admit': "SOFA: CNS (admission)",
        f'renal_admit': "SOFA: Renal (admission)",
        f'sofa_max_{sf_period}': "SOFA (day)",
        f'respiratory_max_{sf_period}': "SOFA: Respiratory (day)",
        f'coagulation_max_{sf_period}': "SOFA: Coagulation (day)",
        f'liver_max_{sf_period}': "SOFA: Liver (day)",
        f'cardiovascular_max_{sf_period}': "SOFA: Cardiovascular (day)",
        f'cns_max_{sf_period}': "SOFA: CNS (day)",
        f'renal_max_{sf_period}': "SOFA: Renal (day)",
        f'fluids_{hr_period}': "Fluids Volume (day)",
        'fluids_volume': "Fluids Volume (whole stay)",
        'fluids_volume_norm_by_los_icu': "Fluids Volume (whole stay, normalized by ICU LOS)",
        'MV_time_abs': "MV Time (duration in the stay, hours)",
        'MV_time_perc_of_stay': "MV Time (duration in the stay, % of ICU LOS)",
        'MV_init_offset_abs': "MV Initiation (offset, hours)",
        'RRT_init_offset_abs': "RRT Initiation (offset, hours)",
        'VP_init_offset_abs': "Vasopressor Initiation (offset, hours)",
        'VP_time_abs': "Vasopressor Time (duration in the stay, hours)",
        'VP_time_perc_of_stay': "Vasopressor Time (duration in the stay, % of ICU LOS)",
        f'FiO2_mean_{hr_period}': "FiO2 (mean %)",
        f'resp_rate_mean_{hr_period}': "Respiratory Rate (mean)",
        f'mbp_mean_{hr_period}': "Mean Blood Pressure (mean)",
        f'temperature_mean_{hr_period}': "Temperature (mean, first 24h)",
        f'spo2_mean_{hr_period}': "SpO2 (%, mean)",
        f'heart_rate_mean_{hr_period}': "Heart Rate (mean)",
        f'po2_min_{hr_period}': "PaO2 (min)",
        f'pco2_max_{hr_period}': "PaCO2 (max)",
        f'ph_min_{hr_period}': "pH (min)",
        f'glucose_max_{hr_period}': "Glucose (max)",
        f'sodium_min_{hr_period}': "Sodium (min)",
        f'potassium_max_{hr_period}': "Potassium (max)",
        f'cortisol_min_{hr_period}': "Cortisol (min)",
        f'hemoglobin_min_{hr_period}': "Hemoglobin (min)",
        f'fibrinogen_min_{hr_period}': "Fibrinogen (min)",
        f'inr_max_{hr_period}': "INR (max)"
        }

    decimals = {
        'admission_age': 0,
        'fluids_volume': 0,
        f'fluids_{hr_period}': 0,
        'SOFA_admit': 0,
        'respiratory_admit': 0,
        'coagulation_admit': 0,
        'liver_admit': 0,
        'cardiovascular_admit': 0,
        'cns_admit': 0,
        'renal_admit': 0,
        'charlson_comorbidity_index': 0,
        f'FiO2_mean_{hr_period}': 0,
        'los_icu_dead': 2,
        'los_icu_surv': 2,
        'los_hosp_dead': 2,
        'los_hosp_surv': 2,
        'MV_time_perc_of_stay': 2,
        'VP_time_perc_of_stay': 2    
        }


    # Create a TableOne 
    table1_s = TableOne(data, columns=categ+nonnorm,
                        rename=labls, limit=limit, order=order, decimals=decimals,
                        groupby=groupby, categorical=categ, nonnormal=nonnorm,
                        missing=True, overall=False,
                        dip_test=True, normal_test=True, tukey_test=True, htest_name=True)

    table1_s.to_excel(f'results/table1_coh{cohort_number}.xlsx')

    # save data for further analysis
    data.to_csv(f'data/clean/MIMIC_coh{cohort_number}', index=False)


cohorts = [1,2,3,4]
hr_periods = ["6_24h", "24_48h", "48_72h", "72_96h"]
sf_periods = ["0_24h", "24_48h", "48_72h", "72_96h"]

for i in range(len(cohorts)):
    print(f"Processing cohort {cohorts[i]}")
    #table_one(cohorts[i], hr_periods[i], sf_periods[i])

tables = []
# Read all tables and merge them with a loop
for i in range(1,5):

    table = pd.read_excel(f'results/table1_coh{i}.xlsx')

    if i == 1:
        # keep just the first 2 columns
        tables.append(table.iloc[:, :2])

    # drop the first 2 columns
    table = table.iloc[:, 2:]

    # make and header with the cohort number
    header = pd.DataFrame([f"Day {i}"] * len(table.columns), index=table.columns).T
    # concatenate the header and the table
    table = pd.concat([header, table], axis=0)

    tables.append(table)

# concatenate in a single table, but index just once
table1 = pd.concat(tables, axis=1)

table1.to_excel('results/table1_all.xlsx', index=False, header=False)
