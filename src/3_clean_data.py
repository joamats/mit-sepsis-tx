import pandas as pd
import numpy as np


def clean_data(cohort_number, hr_period, sf_period):

    data = pd.read_csv(f'data/MIMIC_coh_{cohort_number}.csv')

    rename_dict = {f'sofa_max_{sf_period}': 'sofa_max_day',
                   f'respiratory_max_{sf_period}': 'respiratory_max_day',
                   f'coagulation_max_{sf_period}': 'coagulation_max_day',
                   f'liver_max_{sf_period}': 'liver_max_day',
                   f'cardiovascular_max_{sf_period}': 'cardiovascular_max_day',
                   f'cns_max_{sf_period}': 'cns_max_day',
                   f'renal_max_{sf_period}': 'renal_max_day',
                   f'fluids_{hr_period}': 'fluids_day',
                   f'FiO2_mean_{hr_period}': 'FiO2_mean_day',
                   f'resp_rate_mean_{hr_period}': 'resp_rate_mean_day',
                   f'mbp_mean_{hr_period}': 'mbp_mean_day',
                   f'temperature_mean_{hr_period}': 'temperature_mean_day',
                   f'spo2_mean_{hr_period}': 'spo2_mean_day',
                   f'heart_rate_mean_{hr_period}': 'heart_rate_mean_day',
                   f'po2_min_{hr_period}': 'po2_min_day',
                   f'pco2_max_{hr_period}': 'pco2_max_day',
                   f'ph_min_{hr_period}': 'ph_min_day',
                   f'lactate_max_{hr_period}': 'lactate_max_day',
                   f'glucose_max_{hr_period}': 'glucose_max_day',
                   f'sodium_min_{hr_period}': 'sodium_min_day',
                   f'potassium_max_{hr_period}': 'potassium_max_day',
                   f'cortisol_min_{hr_period}': 'cortisol_min_day',
                   f'hemoglobin_min_{hr_period}': 'hemoglobin_min_day',
                   f'fibrinogen_min_{hr_period}': 'fibrinogen_min_day',
                   f'inr_max_{hr_period}': 'inr_max_day'
                  }

    # Rename variables
    data = data.rename(columns=rename_dict)
    
    # Dictionary with Lower limit, Upper Limit, Normal Range for each of the labs
    lab_ranges = {'po2_min_day': [0, 90, 1000],
                  'pco2_max_day': [0, 40, 200],
                  'ph_min_day': [5, 7.35, 10],
                  'lactate_max_day': [0, 1.05, 30],
                  'glucose_max_day': [0, 95, 2000],
                  'sodium_min_day': [0, 140, 160],
                  'potassium_max_day': [0, 3.5, 9.9],
                  'cortisol_min_day': [0, 20, 70],
                  'fibrinogen_min_day': [0, 200, 1000],
                  'inr_max_day': [0, 1.1, 10],
                  'resp_rate_mean_day': [0, 15, 50],
                  'heart_rate_mean_day': [0, 90, 250],
                  'mbp_mean_day': [0, 85, 200],
                  'temperature_mean_day': [32, 36.5, 45],
                  'spo2_mean_day': [0, 95, 100]
    }

    # Replace 

    for lab in lab_ranges.keys():
        data[lab] = np.where(data[lab] < lab_ranges[lab][0], 0, data[lab])
        data[lab] = np.where(data[lab] > lab_ranges[lab][2], 0, data[lab])
        data[lab] = np.where(data[lab] == 0, lab_ranges[lab][1], data[lab])
        data[lab] = data[lab].fillna(lab_ranges[lab][1])

    # transform the code above into a smarter way, using pandas apply in a row, axis=1
    data['hemoglobin_min_day'] = data['hemoglobin_min_day'].apply(lambda x: 0 if x < 3 else x)
    data['hemoglobin_min_day'] = data['hemoglobin_min_day'].apply(lambda x: 0 if x > 30 else x)
    data['hemoglobin_min_day'] = data['hemoglobin_min_day'].fillna(0)
    data['hemoglobin_min_day'] = data.apply(lambda row: 12 if (row.hemoglobin_min_day == 0) \
                                                            & (row.sex_female == 1) \
                                                          else row.hemoglobin_min_day, axis=1)
    
    data['hemoglobin_min_day'] = data.apply(lambda row: 13.5 if (row.hemoglobin_min_day == 0) \
                                                              & (row.sex_female == 0) \
                                                            else row.hemoglobin_min_day, axis=1)
        
    # impute SOFA as 0 if missing using apply lambda
    sofa_cols = ['sofa_max_day', 'respiratory_max_day', 'cardiovascular_max_day',
                 'cns_max_day', 'renal_max_day', 'liver_max_day', 'coagulation_max_day', 
                 'SOFA_admit', 'respiratory_admit', 'cardiovascular_admit',
                 'cns_admit', 'renal_admit', 'liver_admit', 'coagulation_admit']
    
    for col in sofa_cols:
        data[col] = data[col].fillna(0)

    # encode Absent as 0
    data['ckd_stages'] = data['ckd_stages'].apply(lambda x: 0 if x == "Absent" else x).astype(float)
    data['diabetes_types'] = data['diabetes_types'].apply(lambda x: 0 if x == "Absent" else x)
    # transform CKD stage into a categorical variable
    data['ckd_stages'] = data.ckd_stages.apply(lambda x: 1 if x > 2 else 0)

    # Replace missing values in fluids_day by 0
    data['fluids_day'] = data['fluids_day'].fillna(0)
    
    # replace not nan values by 1
    com_cols = ['hypertension_present', 'heart_failure_present', 'copd_present',
                'asthma_present', 'cad_present', 'connective_disease']

    for col in com_cols:
        data[col] = data[col].apply(lambda x: 0 if x != 1 else 1)

    # encode race_white into dummy
    data['race_white'] =  data['race_white'].apply(lambda x: 1 if x == "White" else 0)

    # encode proficieny in english into dummy
    data['eng_prof'] = data['eng_prof'].apply(lambda x: 1 if x == "Proficient" else 0)

    # encode anchor_year_group as numeric
    map_dict = {"2008 - 2010": 0, "2011 - 2013": 1, "2014 - 2016": 2, "2017 - 2019": 3}
    data['anchor_year_group'] = data['anchor_year_group'].map(map_dict)

    data = data[
                ['admission_age', 'sex_female', 'race_white', 'eng_prof', 'private_insurance'] + \
                ['anchor_year_group', 'adm_elective', 'major_surgery'] + \
                ['charlson_comorbidity_index'] + \
                ['SOFA_admit', 'respiratory_admit', 'cardiovascular_admit', 'cns_admit', 'renal_admit', 'liver_admit'] + \
                com_cols + ['ckd_stages'] + \
                list(rename_dict.values()) + \
                ['MV_elig_day','MV_elig1', 'MV_elig2', 'MV_elig3', 'MV_elig4',
                 'RRT_elig_day','RRT_elig1', 'RRT_elig2', 'RRT_elig3', 'RRT_elig4',
                 'VP_elig_day','VP_elig1', 'VP_elig2', 'VP_elig3', 'VP_elig4'] + \
                 ['pneumonia', 'uti', 'biliary', 'skin']
    ]

    # get rename_dict values in list

    data.to_csv(f'data/clean/coh_{cohort_number}.csv', index=False)

# Main
cohorts = [1,2,3,4]
hr_periods = ["6_24h", "24_48h", "48_72h", "72_96h"]
sf_periods = ["0_24h", "24_48h", "48_72h", "72_96h"]
hr_bounds  = [[0,24], [24,48], [48,72], [72,96]]

for i in range(len(cohorts)):
    print(f"Processing cohort {cohorts[i]}...")
    clean_data(cohorts[i], hr_periods[i], sf_periods[i])
