import pandas as pd
from matplotlib import pyplot as plt

import matplotlib
matplotlib.use('TKAgg')

def plot_results(filename, model_name):
    # load data from csv file into pandas dataframe
    data = pd.read_csv(f"results/models/{filename}.csv")

    # group data by treatment type
    treatment_groups = data.groupby("treatment")

    # Set the figure and axes
    fig, axes = plt.subplots(1, 3,
                            sharex=True, sharey=True,
                            figsize=(9,3.5))

    fig.suptitle(f'{model_name} Model: Likelihood of Treatment Initiation')

    # create dictionary of name for each treatment group
    treatment_names = {"MV_elig": "Mechanical Ventilation",
                    "RRT_elig": "RRT",
                    "VP_elig": "Vasopressor(s)"
    }

    # set common horizontal line at 1 for all subplots
    for ax in axes:
        ax.axvline(x=1, linewidth=0.8, linestyle='--', color='black')

    # loop over treatment groups and create a subplot for each
    for (treatment, group), ax in zip(treatment_groups, axes):
        # plot odds ratios with confidence intervals as error bars
        ax.errorbar(x=group["OR"],
                    y=group["cohort"],
                    xerr=[group["OR"] - group["2.5%"], group["97.5%"] - group["OR"]],
                    fmt='o',
                    capsize=3)
        # set subplot title
        ax.set_title([treatment_names[treatment]][0])
        # set xrange to breath a bit
        ax.set_ylim([.5, 4.5])
        # set yrange to
        ax.set_xlim([0.5, 1.5])
        # set xticks in string format
        ax.set_yticks([1,2,3,4])
        ax.set_yticklabels(["1", "2", "3", "4"])
        ax.set_xlabel("Favours White | Favours R.E.G",
                    fontsize=8, labelpad=5, color='gray')


    fig.supxlabel('Odds Ratio (95% CI)')
    fig.supylabel('Cohort Number')
    plt.tight_layout()

    # Save the figure
    #fig.savefig(f"results/plots/{filename}.png", dpi=300, bbox_inches="tight")
    fig.savefig(f"results/plots/{filename}.jpeg", dpi=600, bbox_inches="tight")


filenames = ["sens/logreg_cv_all_coh", "sens/xgb_cv_all_coh",
             "logreg_cv_all_coh", "xgb_cv_all_coh"]
model_names = ["Logistic Regression", "XGBoost",
               "Logistic Regression", "XGBoost"]

for f, m in zip(filenames, model_names):
    plot_results(f, m)
