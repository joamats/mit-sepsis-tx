import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from joblib import Parallel, delayed
import multiprocessing

# Set number of processes to run in parallel
num_processes = 5

# Function to train the logistic regression model and calculate OR for a fold
def train_model(train_index, test_index):
    _, X_test = X.iloc[train_index,:], X.iloc[test_index,:]
    _, y_test = y.iloc[train_index], y.iloc[test_index]

    # Fit logistic regression model
    model = LogisticRegression(max_iter=10000)
    model.fit(X_test, y_test)

    idx = X_test.columns.get_loc(race)
    param = model.coef_[0][idx]
    OR_inner = np.exp(param)

    return OR_inner

setting = "sens/logreg_cv_all_coh"

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
        data = pd.read_csv(f"data/sens/clean/coh_{cohort}_{treatment[:-5]}.csv")

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

                # Normal k-fold cross-validation
                kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=i)

                # Inner loop, in each fold, running in parallel
                ORs = Parallel(n_jobs=num_processes)(
                    delayed(train_model)(train_index, test_index)
                    for train_index, test_index in tqdm(kf.split(X, r))
                )

                # Calculate odds ratio based on all 5 folds
                odds_ratio = np.mean(ORs)
                odds_ratios.append(odds_ratio)

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
            results_df.to_csv(f"results/models/{setting}.csv", index=False)
