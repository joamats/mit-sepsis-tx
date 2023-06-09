import pandas as pd
from matplotlib import pyplot as plt

import matplotlib
matplotlib.use('TKAgg')


def plot_results(filename, model_name):

    # load data from csv file into pandas dataframe
    data = pd.read_csv(f"results/models/{filename}.csv")

    # group data by treatment type
    treatment_groups = data.groupby("treatment")

    races = ['race_white','race_black', 'race_hisp', 'race_asian']
    races_names = ['White','Black', 'Hispanic', 'Asian']
    ws = [.6, .2, -.2, -.6,]

    # Set the figure and axes
    fig, axes = plt.subplots(1, 3,
                            sharex=True, sharey=True,
                            figsize=(12,4.5))

    fig.suptitle(f'{model_name} Model: Likelihood of Treatment Initiation')

    # create dictionary of name for each treatment group
    treatment_names = {"MV_elig": "Mechanical Ventilation",
                    "RRT_elig": "RRT",
                    "VP_elig": "Vasopressor(s)"
    }

    # set common horizontal line at 1 for all subplots
    for i, ax in enumerate(axes):
        ax.axvline(x=1, linewidth=0.8, linestyle='--', color='black')

    # loop over treatment groups and create a subplot for each
    for (treatment, groups), ax in zip(treatment_groups, axes):
        # plot odds ratios with confidence intervals as error bars
        for i in range(len(races)):

            name = races_names[i]
            w = ws[i]
            group = groups[groups.race == races[i]]

            ax.errorbar(group["OR"],
                        group["cohort"]*3 + w,
                        xerr=[group["OR"] - group["2.5%"], group["97.5%"] - group["OR"]],
                        label=name,
                        fmt='o',
                        linewidth=.5,
                        capsize=3)
        # set subplot title
        ax.set_title([treatment_names[treatment]][0])
        # set yrange to breath a bit
        ax.set_ylim([1.5, 13.5])
        # set xrange to
        ax.set_xlim([.5, 1.5])
        # set yticks in string format
        ax.set_yticks([3,6,9,12])
        ax.set_yticklabels(["1", "2", "3", "4"])
        ax.set_xlabel("Favours White | Favours R.E.G",
                    fontsize=8, labelpad=5, color='gray')
        
    # add horizontal lines to all axes, per y tick
    for ax in axes:
        for y in [3,6,9]:
            ax.axhline(y+1.5, color='gray', linestyle='-', linewidth=.5)
        

    # add legend
    axes[2].legend(loc='upper left', bbox_to_anchor=(1.05, .7),
                title="Race-Ethnicity")
    # add title to legend

    fig.supxlabel('Odds Ratio (95% CI)')
    fig.supylabel('Cohort Number')
    plt.tight_layout()

    # Save the figure
    #fig.savefig(f"results/plots/{filename}.png", dpi=300, bbox_inches="tight")
    fig.savefig(f"results/plots/{filename}.jpeg", dpi=600, bbox_inches="tight")

filenames = ["sens/logreg_cv_all_coh_races", "sens/xgb_cv_all_coh_races",
             "logreg_cv_all_coh_races", "xgb_cv_all_coh_races"]
model_names = ["Logistic Regression", "XGBoost",
               "Logistic Regression", "XGBoost"]

for f, m in zip(filenames, model_names):
    plot_results(f, m)