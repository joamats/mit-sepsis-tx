import pandas as pd
import numpy as np
from sklearn.utils import resample
import shap
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TKAgg')

setting = "all_coh_races"

# create a function to calculate odds ratio from SHAP values
def calc_odds_ratio(shap_values, feature):

    # subfunction to calculate odds ratio
    def calc_OR(shap_values, feature):
        control_group = shap_values[(data[feature] == 0)].mean()
        study_group   = shap_values[(data[feature] == 1)].mean()

        return np.exp(study_group[feature]) / np.exp(control_group[feature])
    
    # calculate odds ratio, based on all data
    OR = calc_OR(shap_values, feature)

    # bootsrap for confidence intervals
    OR_bootstrap = []
    n_replicates = 1000

    # perform bootstrap sampling and calculate odds ratio for each replicate
    for i in range(n_replicates):
        sample = resample(shap_values, replace=True, n_samples=len(shap_values))
        OR_bootstrap.append(calc_OR(sample, feature))

    # calculate confidence intervals
    CI_lower = np.percentile(OR_bootstrap, 2.5)
    CI_upper = np.percentile(OR_bootstrap, 97.5)

    return OR, CI_lower, CI_upper

# now read treatment from txt
with open("config/treatments.txt", "r") as f:
    treatments = f.read().splitlines()
treatments.remove("treatment")

# read features from list in txt
with open("config/confounders_races.txt", "r") as f:
    confounders = f.read().splitlines()
confounders.remove("confounder")

# create dataframes to store results
results_df = pd.DataFrame(columns=["cohort","race","treatment","OR","2.5%","97.5%"])

cohorts = [1,2,3,4]
races = ['race_black', 'race_hisp', 'race_asian']

for cohort in cohorts:
    print(f"Cohort: {cohort}")

    for treatment in treatments:
        print(f"Treatment: {treatment}")
        # load data
        data = pd.read_csv(f"data/clean/coh_{cohort}_{treatment[:-5]}.csv")

        # add to results_df the race_white as reference
        results_df = results_df.append({"cohort": cohort,
                                        "race": "race_white",
                                        "treatment": treatment,
                                        "OR": 1,
                                        "2.5%": 1,
                                        "97.5%": 1}, ignore_index=True)

        for race in races:
            print(f"Race-Ethnicity: {race}")

            # append treatments that are not the current one to confounders
            # select X, y
            conf = confounders + [t for t in treatments if t != treatment] + [race]
            X = data[conf]
            y = data[treatment]

            model = XGBClassifier()
            model.fit(X, y)

            # shap explainer
            explainer = shap.TreeExplainer(model, X)
            shap_values = explainer(X, check_additivity=False)

            shap_values = pd.DataFrame(shap_values.values, columns=conf)

            # calculate odds ratios, CI 
            OR, CI_lower, CI_upper = calc_odds_ratio(shap_values, race)

            print(f"OR (95% CI): {OR:.3f} ({CI_lower:.3f} - {CI_upper:.3f})")

            # append results to dataframe
            results_df = results_df.append({"cohort": cohort,
                                            "race": race,
                                            "treatment": treatment,
                                            "OR": OR,
                                            "2.5%": CI_lower,
                                            "97.5%": CI_upper}, ignore_index=True)
            # save results as we go
            results_df.to_csv(f"results/models/xgb_{setting}.csv", index=False)
