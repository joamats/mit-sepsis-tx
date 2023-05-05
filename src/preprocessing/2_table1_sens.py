from tableone import TableOne
import pandas as pd

def table_one(cohort_number, hr_period, sf_period, hr_bound):

    data = pd.read_csv(f'data/sens/MIMIC_coh_{cohort_number}.csv')


    # Create a TableOne 
    table1_s = TableOne(data, columns=categ+nonnorm,
                        rename=labls, limit=limit, order=order, decimals=decimals,
                        groupby=groupby, categorical=categ, nonnormal=nonnorm,
                        missing=True, overall=False,
                        dip_test=True, normal_test=True, tukey_test=True, htest_name=True)

    table1_s.to_excel(f'results/table1/coh_{cohort_number}.xlsx')

    # save data for further analysi
    data.to_csv(f'data/MIMIC_coh_{cohort_number}.csv', index=False)


cohorts = [1,2,3,4]
hr_bounds = [24, 48, 72, 96]

for i in range(len(cohorts)):
    print(f"Processing cohort {cohorts[i]}...")
    table_one(cohorts[i], "6_24h", "0_24h", hr_bounds[i])

tables = []
# Read all tables and merge them with a loop
for i in range(1,5):

    table = pd.read_excel(f'results/table1/coh_{i}.xlsx')

    if i == 1:
        # keep just the first 2 columns
        tables.append(table.iloc[:, :2])

    # drop the first 2 columns
    table = table.iloc[:, 2:]

    # make and header with the cohort number
    header = pd.DataFrame([f"Up to Day {i}"] * len(table.columns), index=table.columns).T
    # concatenate the header and the table
    table = pd.concat([header, table], axis=0)

    tables.append(table)

# concatenate in a single table, but index just once
table1 = pd.concat(tables, axis=1)

table1.to_excel('results/table1/sens/all.xlsx', index=False, header=False)
