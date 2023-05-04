import pandas as pd
import numpy as np
import shap
from tqdm import tqdm
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold

setting = "cv_all_coh"

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
with open("config/confounders.txt", "r") as f:
    confounders = f.read().splitlines()
confounders.remove("confounder")

# create dataframes to store results
results_df = pd.DataFrame(columns=["cohort","race","treatment","OR","2.5%","97.5%"])

cohorts = [1,2,3,4]
races = ['race_nonwhite']

for cohort in cohorts:
    print(f"Cohort: {cohort}")

    for treatment in treatments:
        print(f"Treatment: {treatment}")
        # load data
        data = pd.read_csv(f"data/clean/coh_{cohort}_{treatment[:-5]}.csv")

        for race in races:
            print(f"Race-Ethnicity: {race}")

            # append treatments that are not the current one to confounders
            # select X, y
            conf = confounders + [t for t in treatments if t != treatment] 

            # compute OR based on all data
            X = data[conf]
            y = data[treatment]
            r = data[race]

            n_rep = 100
            odds_ratios = []

            # outer loop
            for i in tqdm(range(n_rep)):

                # list to append inner ORs
                ORs = []

                # normal k-fold cross validation
                kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=i)

                # inner loop, in each fold
                for train_index, test_index in tqdm(kf.split(X, r)):
                    X_train, X_test = X.iloc[train_index,:], X.iloc[test_index,:]
                    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

                    model = XGBClassifier()
                    model.fit(X_test, y_test)

                    # shap explainer
                    explainer = shap.TreeExplainer(model, X_test)
                    shap_values = explainer(X_test, check_additivity=False)

                    shap_values = pd.DataFrame(shap_values.values, columns=conf)

                    OR_inner = calc_OR(shap_values, X_test.reset_index(drop=True), race)
                    # append OR to list
                    ORs.append(OR_inner)

                    print(f"OR: {OR_inner:.5f}")

                # calculate odds ratio based on all 5 folds, append
                odds_ratios.append(np.mean(ORs))

            # calculate confidence intervals
            CI_lower = np.percentile(odds_ratios, 2.5)
            OR = np.percentile(odds_ratios, 50)
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
