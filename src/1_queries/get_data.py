import os
from dotenv import load_dotenv
from google.cloud import bigquery
import pandas as pd
from argparse import ArgumentParser


def create_aux_dataset(client, project_id):
    # Create 'aux' dataset if it doesn't exist
    dataset_id = f"{project_id}.my_MIMIC"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "US"
    print(f"Creating dataset {dataset_id}...")
    dataset = client.create_dataset(dataset, exists_ok=True)


def create_aux_tables(client,
                      project_id,
                      script_filenames=['src/queries/pivoted/pivoted_codes.SQL',
                                        'src/queries/pivoted/pivoted_comorbidities.SQL',
                                        'src/queries/vitals/vital_day1.SQL',
                                        'src/queries/vitals/vital_day2.SQL',
                                        'src/queries/vitals/vital_day3.SQL',
                                        'src/queries/vitals/vital_day4.SQL',
                                        'src/queries/labs/lab_day1.SQL',
                                        'src/queries/labs/lab_day2.SQL',
                                        'src/queries/labs/lab_day3.SQL',
                                        'src/queries/labs/lab_day4.SQL',
                                        'src/queries/bg/bg_day1.SQL',
                                        'src/queries/bg/bg_day2.SQL',
                                        'src/queries/bg/bg_day3.SQL',
                                        'src/queries/bg/bg_day4.SQL',
                                        'src/queries/bg_art/bg_art_day1.SQL',
                                        'src/queries/bg_art/bg_art_day2.SQL',
                                        'src/queries/bg_art/bg_art_day3.SQL',
                                        'src/queries/bg_art/bg_art_day4.SQL']):
    # Run SQL scripts in order
    for script_filename in script_filenames:
        print(f"Executing {script_filename}...")
        with open(script_filename, 'r') as script_file:
            script = script_file.read().replace("physionet-data", project_id).replace("db_name", project_id, -1)
            job = client.query(script)
            job.result()  # Wait for the query to complete


def create_main_table(client, project_id, destination):
    print(f"Creating main table {destination}...")
    with open('src/queries/main.SQL', 'r') as script_file:
        script = script_file.read().replace("physionet-data", project_id).replace("db_name", project_id, -1)
        df = client.query(script).to_dataframe()
        df.to_csv(destination, index=False)


def main(args):
    # Load environment variables
    load_dotenv()
    project_id = os.getenv('PROJECT_ID')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv("KEYS_FILE")
    # Set up BigQuery client using default SDK credentials
    client = bigquery.Client(project=project_id)
    # create the aux dataset
    create_aux_dataset(client, project_id)
    # create the aux tables
    create_aux_tables(client, project_id)
    # create the main table
    create_main_table(client, project_id, args.destination)


if __name__ == "__main__":
    # parse the arguments
    parser = ArgumentParser()
    parser.add_argument(
        "-d", "--destination", default='data/MIMIC_data.csv', help="output csv file")
    args = parser.parse_args()
    main(args)
