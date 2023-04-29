import pandas as pd
import numpy as np
import os
from utils import get_demography, print_demo

df0 = pd.read_csv('data/MIMIC_data.csv')
demo0 = print_demo(get_demography(df0))
print(f"{len(df0)} MIMIC-IV ICU stays \n({demo0})\n")

# Remove patients without sepsis
df1 = df0[df0.sepsis3 == True]
print(f"Removed {len(df0) - len(df1)} stays without sepsis")
demo1 = print_demo(get_demography(df1))
print(f"{len(df1)} sepsis stays \n({demo1})\n")

# Remove patiens without Full Code on admission (only)
df2 = df1[(df1.is_full_code_admission == 1)]
print(f"Removed {len(df1) - len(df2)} stays without Full Code (admission only)")
demo2 = print_demo(get_demography(df2))
print(f"{len(df2)} stays with sepsis and Full Code on admission \n({demo2})\n")

# Create 4 new cohorts, iterating, removing patients with LoS < 2 day , 3 days, 4 days, 5 days
for los_min in range(2, 6):
    # Remove patients with LoS < {los_min} days
    print(f"\nRamification Starts for Cohort {los_min-1}\n")
    df3 = df2[df2.los_icu >= los_min]
    print(f"Removed {len(df2) - len(df3)} stays with LoS < {los_min} days")
    demo3 = print_demo(get_demography(df3))
    print(f"{len(df3)} stays with sepsis, ICU LoS >= {los_min} days, \n({demo3})\n")

    # Remove patients with recurrent stays
    df4 = df3.sort_values(by=["subject_id", "hadm_id", "hospstay_seq","icustay_seq"], ascending=True) \
             .groupby('subject_id') \
             .apply(lambda group: group.iloc[0, 1:])

    print(f"Removed {len(df3) - len(df4)} recurrent stays")
    demo4 = print_demo(get_demography(df4))
    print(f"{len(df4)} stays with sepsis, ICU LoS >= {los_min} days, full code \n({demo4})\n")

    df4.to_csv(f'data/MIMIC_coh_{los_min-1}.csv')
    