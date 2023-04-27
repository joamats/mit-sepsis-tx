import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from tqdm import tqdm

import matplotlib
matplotlib.use('TKAgg')

# load data from csv file into pandas dataframe
data = pd.read_csv("results/models/logistic_reg.csv")

# group data by treatment type
treatment_groups = data.groupby("treatment")

# Set the figure and axes
fig, axes = plt.subplots(1, 3,
                         sharex=True, sharey=True,
                         figsize=(8.25,3.5))

fig.suptitle('Likelihood of Receiving a Treatment, per Day of Initiation')
axes[0].set_ylabel("Odds Ratio (95% CI)\n White vs. Racial-Ethnic Group")

# create dictionary of name for each treatment group
treatment_names = {"MV_elig_day": "Mechanical Ventilation",
                   "RRT_elig_day": "RRT",
                   "VP_elig_day": "Vasopressor(s)"
}

# set common horizontal line at 1 for all subplots
for ax in axes:
    ax.axhline(y=1, linewidth=0.8, linestyle='--', color='black')

# loop over treatment groups and create a subplot for each
for (treatment, group), ax in zip(treatment_groups, axes):
    # plot odds ratios with confidence intervals as error bars
    ax.errorbar(group["cohort"],
                group["OR"],
                yerr=[group["OR"] - group["2.5%"], group["97.5%"] - group["OR"]],
                fmt='o',
                capsize=3)
    # set subplot title
    ax.set_title([treatment_names[treatment]][0])
    # set xrange to breath a bit
    ax.set_xlim([.5, 4.5])
    # set xticks
    ax.set_xticks([1, 2, 3, 4])

fig.supxlabel('Day of Treatment Initiation')
plt.tight_layout()

# Save the figure
fig.savefig(f"results/plots/logistic_reg.png", dpi=300, bbox_inches="tight")
