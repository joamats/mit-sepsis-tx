# mit-sepsis-tx

Likelihood of Receiving a Treatment, across Race-Ethnicity for Septic Patients in the ICU

The goal of this project is to investigate disparities between races in critically ill sepsis patients in regard to likelihood of receiving one of three life-sustaining treatmens, i.e. renal replacement therapy (RRT), vasopressor use (VP), or mechanical ventilation (MV) in cohorts curated from MIMIC IV (2008-2019).

## How to run this project

### 1. Clone this repository

Run the following command in your terminal.

```sh
git clone https://github.com/joamats/mit-sepsis-tx.git
```

### 2. Install required Packages

Run the following command:

```sh
pip install -r src/setup/requirements.txt
```

### 3. Fetch the data

MIMIC data can be found in [PhysioNet](https://physionet.org/), a repository of freely-available medical research data, managed by the MIT Laboratory for Computational Physiology. Due to its sensitive nature, credentialing is required to access both datasets.

Documentation for MIMIC-IV's can be found [here](https://mimic.mit.edu/).

#### Integration with Google Cloud Platform (GCP)

In this section, we explain how to set up GCP and your environment in order to run SQL queries through GCP right from your local Python setting. Follow these steps:

1) Create a Google account if you don't have one and go to [Google Cloud Platform](https://console.cloud.google.com/bigquery)
2) Enable the [BigQuery API](https://console.cloud.google.com/apis/api/bigquery.googleapis.com)
3) Create a [Service Account](https://console.cloud.google.com/iam-admin/serviceaccounts), where you can download your JSON keys
4) Place your JSON keys in the parent folder (for example) of your project
5) Create a .env file with the command `cp env.example env `
6) Update your .env file with your ***JSON keys*** path and the ***id*** of your project in BigQuery

#### MIMIC-IV

After getting credentialing at PhysioNet, you must sign the data use agreement and connect the database with GCP, either asking for permission or uploading the data to your project.

Having all the necessary tables for the cohort generation query in your project (you have to run all the auxillary queries manually on BigQuery), run the following command to fetch the data as a dataframe that will be saved as CSV in your local project. Make sure you have all required files and folders.

```sh
python3 src/py_scripts/get_data.py --sql "src/sql_queries/main.sql" --destination "data/MIMIC_data.csv"
```

And transform into a ready to use dataframe by running all scripts in 2_preprocessing sequentially.

The ICD-9 to ICD-10 translation based on this [GitHub Repo](https://github.com/AtlasCUMC/ICD10-ICD9-codes-conversion).

### 4. Run the analyses

Run the scripts in 3_models.
