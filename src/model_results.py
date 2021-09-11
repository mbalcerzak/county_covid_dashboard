from posixpath import dirname
from random import sample
import pandas as pd
import os
import json
from collections import defaultdict


def get_sample_counties_list():
    path = 'data/sample/sample_counties_list.json'

    with open(path, 'r') as f:
        return json.load(f)


def get_predictions():
    """Loads predictions from a selected model from ReichlabCovidPredictions"""
    folder_path = '/Users/malgorzatabslcerzak/Documents/projects/covid19-forecast-hub/data-processed/CEID-Walk'
    file_list = [x for x in os.listdir(folder_path) if '.csv' in x]

    sample_counties = get_sample_counties_list()
    county_predicted_cases_sample = defaultdict(dict)

    for file in file_list:
        df = pd.read_csv(f"{folder_path}/{file}")
        df = df.loc[(df['target'] == '4 wk ahead inc case') & (df['type'] == 'point')]

        # For sample counties only
        df['location'] = df['location'].apply(lambda x: x.lstrip('0'))
        df = df.loc[df['location'].isin(sample_counties)]

        for county in sample_counties:
            data = df[df['location'] == county]

            for date in data['target_end_date']:
                value = data['value'].loc[data['target_end_date'] == date]
                value = list(value)[0]

                county_predicted_cases_sample[county][date] = value

    with open('data/sample/county_predicted_cases_sample.json', 'w') as f:
        json.dump(county_predicted_cases_sample, f)


if __name__ == "__main__":
    get_predictions()