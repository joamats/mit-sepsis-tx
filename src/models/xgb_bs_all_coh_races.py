import pandas as pd
import numpy as np
from sklearn.utils import resample
import shap
from tqdm import tqdm
from xgboost import XGBClassifier

setting = "bs_all_coh_races"

# function to calculate odds ratio
def calc_OR(shap_values, data, feature):
    control_group = shap_values[(data[feature] == 0)].mean()
    study_group   = shap_values[(data[feature] == 1)].mean()

    return np.exp(study_group[feature]) / np.exp(control_group[feature])


# now read treatment from txt
with open("config/treatments.txt", "r") as f:
    treatments = f.read().splitlines()
treatments.remove("treatment")

# read features from list in txt
with open("config/confounders_race.txt", "r") as f:
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

        # append results to dataframe
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

            # compute OR based on all data
            X = data[conf]
            y = data[treatment]

            model = XGBClassifier()
            model.fit(X, y)

            # shap explainer
            explainer = shap.TreeExplainer(model, X)
            shap_values = explainer(X, check_additivity=False)

            shap_values = pd.DataFrame(shap_values.values, columns=conf)

            # calculate odds ratios
            OR = calc_OR(shap_values, data, race)

            n_rep = 20
            odds_ratios = []

            for i in tqdm(range(n_rep)):

                # bootsrap the data
                sample = resample(data, replace=True, n_samples=len(data)).reset_index(drop=True)
                
                X = sample[conf]
                y = sample[treatment]

                model = XGBClassifier()
                model.fit(X, y)

                # shap explainer
                explainer = shap.TreeExplainer(model, X)
                shap_values = explainer(X, check_additivity=False)

                shap_values = pd.DataFrame(shap_values.values, columns=conf)

                # calculate odds ratios
                odds_ratios.append(calc_OR(shap_values, sample, race))

            # calculate confidence intervals
            CI_lower = np.percentile(odds_ratios, 2.5)
            CI_upper = np.percentile(odds_ratios, 97.5)

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
