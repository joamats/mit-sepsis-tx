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
                         figsize=(8.25,3),
                         constrained_layout=True)

# set common horizontal line at 1 for all subplots
for ax in axes:
    ax.axhline(y=1, linestyle='--', color='grey')

# loop over treatment groups and create a subplot for each
for (treatment, group), ax in zip(treatment_groups, axes):
    # plot odds ratios with confidence intervals as error bars
    ax.errorbar(group["cohort"], group["OR"], yerr=[group["OR"] - group["2.5%"], group["97.5%"] - group["OR"]], fmt='o', capsize=5)
    # set subplot title
    ax.set_title(treatment)
    # set x-axis label
    ax.set_xlabel("Cohort")
    # set y-axis label
    ax.set_ylabel("Odds Ratio (95% CI))")

# Save the figure
fig.savefig(f"results/plots/logistic_reg.png", dpi=300, bbox_inches="tight")
