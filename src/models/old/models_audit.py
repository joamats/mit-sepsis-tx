import pandas as pd
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, brier_score_loss

# read features from list in txt
with open("config/confounders.txt", "r") as f:
    confounders = f.read().splitlines()
confounders.remove("confounder")

# now read treatment from txt
with open("config/treatments.txt", "r") as f:
    treatments = f.read().splitlines()
treatments.remove("treatment")

results_df = pd.DataFrame(columns=["cohort","treatment",
                                   "model","converged",
                                   "AUC","Brier"])

cohorts = [1,2,3,4]

for cohort in cohorts:
    print(f"Cohort: {cohort}")

    for treatment in treatments:
        print(f"Treatment: {treatment}")
        # load data
        data = pd.read_csv(f"data/clean/coh_{cohort}_{treatment[:-5]}.csv")

        conf = confounders + [t for t in treatments if t != treatment] 

        # load data
        X = data[conf]
        y = data[treatment]

        # split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                            test_size=.2,
                                                            random_state=42)

        # fit model no training data
        model = XGBClassifier()
        model.fit(X_train, y_train)

        # AUC & Brier score
        y_pred_proba = model.predict_proba(X_test)[:,1]
        auc = roc_auc_score(y_test, y_pred_proba)
        brier = brier_score_loss(y_test, y_pred_proba)

        # append results to dataframe
        results_df = results_df.append({"cohort": cohort,
                                        "treatment": treatment,
                                        "model": "XGBoost",
                                        "converged": "",
                                        "AUC": auc,
                                        "Brier": brier}, ignore_index=True)

        # Now Logistic Regression
        model = LogisticRegression(max_iter=10000)
        model.fit(X_train, y_train)

        converged_ = model.n_iter_ #< model.max_iter

        # AUC & Brier score
        y_pred_proba = model.predict_proba(X_test)[:,1]
        auc = roc_auc_score(y_test, y_pred_proba)
        brier = brier_score_loss(y_test, y_pred_proba)

        # append results to dataframe
        results_df = results_df.append({"cohort": cohort,
                                        "treatment": treatment,
                                        "model": "LogReg",
                                        "converged": converged_[0],
                                        "AUC": auc,
                                        "Brier": brier}, ignore_index=True)
        
        results_df.to_csv("results/models_audit.csv", index=False)

