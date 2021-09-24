from genericpath import isdir
import pandas as pd
import os
import json
from collections import defaultdict
from utils import covid_repo_path, get_counties_population


def get_sample_counties_list():
    path = 'data/sample/sample_counties_list.json'
    with open(path, 'r') as f:
        return json.load(f)


def get_predictions():
    """Loads predictions from a selected model from ReichlabCovidPredictions"""
    folder_path = f'{covid_repo_path()}/data-processed'
    model_list_path = 'data/model_list.json'

    with open(model_list_path,'r') as f:
        model_list = json.load(f)

    sample_counties = get_sample_counties_list()
    populations = get_counties_population()

    for model in model_list:
        file_list = [x for x in os.listdir(f'{folder_path}/{model}') if '.csv' in x]
        county_predicted_cases_sample = defaultdict(dict)
        county_predicted_cases_prc = defaultdict(dict)

        for file in file_list:
            df = pd.read_csv(f"{folder_path}/{model}/{file}")
            df = df.loc[(df['target'] == '4 wk ahead inc case') & (df['type'] == 'point')]

            # For sample counties only
            df['location'] = df['location'].apply(lambda x: str(x).lstrip('0'))
            df = df.loc[df['location'].isin(sample_counties)]

            for county in sample_counties:
                data = df[df['location'] == county]

                for date in data['target_end_date']:
                    value = data['value'].loc[data['target_end_date'] == date]
                    value = list(value)[0]

                    county_predicted_cases_sample[county][date] = value
                    county_predicted_cases_prc[county][date] = float(value)*10000 / float(populations[county])

        if len(county_predicted_cases_sample) > 0:
            if set(sample_counties).issubset(set(county_predicted_cases_sample)):
                print(f"All counties found {model}")
                with open(f'data/sample/model_results/{model}.json', 'w') as f:
                    json.dump(county_predicted_cases_sample, f)
                with open(f'data/sample/model_results/{model}_prc.json', 'w') as f:
                    json.dump(county_predicted_cases_prc, f)
            else:
                print(f"Not all counties found {model}")
        else:
            print(f"Empty county dict {model}")


def get_model_list():
    """Include onluy models that have data for '4 wk ahead inc case' """
    folder_path = f'{covid_repo_path()}/data-processed'
    folder_list = [x for x in os.listdir(folder_path) if isdir(f'{folder_path}/{x}')]

    with open('data/licenses.json', 'r') as f:
        licenses = json.load(f)
    
    model_list = []

    acceptable_licenses = ["cc-by-4.0", "mit", "apache-2.0", "gpl-3.0"]
    model_ok_license = [x for x in folder_list if licenses[x] in acceptable_licenses]

    print(f"{len(model_ok_license)} models have acceptable license out of {len(folder_list)}")

    for model in model_ok_license:
        file_list = [x for x in os.listdir(f"{folder_path}/{model}") if '.csv' in x]
        if file_list:
            file = file_list[0]
            df = pd.read_csv(f"{folder_path}/{model}/{file}")
            df = df.loc[(df['target'] == '4 wk ahead inc case') & (df['type'] == 'point')]

        if len(df):
            model_list.append(model)

    with open(f'data/model_list.json', 'w') as f:
        json.dump(model_list, f)  


def get_model_licenses():
    """Include onluy models that allow for commercial use"""
    folder_path = f'{covid_repo_path()}/data-processed'
    folder_list = [x for x in os.listdir(folder_path) if isdir(f'{folder_path}/{x}')]
  
    licenses = {}

    for folder in folder_list:
        file_list = [x for x in os.listdir(f"{folder_path}/{folder}") if '.txt' in x]

        for file in file_list:
            with open(f"{folder_path}/{folder}/{file}",'r') as f:
                for line in  f.readlines():
                    if 'license:' in line:
                        print(f"{folder} --- {line}")

                        licenses[folder] = line.split(':')[-1].replace('\n','').strip()


    with open('data/licenses.json', 'w') as f:
        json.dump(licenses, f)


def get_mae():
    with open('data/counties_true_cases.json', 'r') as f:
        true = json.load(f)

    with open('data/model_list.json','r') as f:
        model_list = json.load(f)

    mae_dict = defaultdict(dict)
    mse_dict = defaultdict(dict)

    for model in model_list:
        try:
            with open(f'data/sample/model_results/{model}.json', 'r') as f:
                pred = json.load(f)

            for county in pred:
                pred_ = pred[county]
                true_ = true[county]

                common_dates = [x for x in pred_ if x in true_]

                if len(common_dates) > 0:
                    mae_dict[county][model] = round(sum([abs(pred_[p_key] - true_[p_key]) for p_key in common_dates])/len(common_dates), 2)
                    mse_dict[county][model] = round(sum([(pred_[p_key] - true_[p_key])**2 for p_key in common_dates])/len(common_dates), 2)
            
        except FileNotFoundError:
            pass

        print(mae_dict)
        print(mse_dict)

    with open(f'data/mae.json', 'w') as f:
        json.dump(mae_dict, f)  

    with open(f'data/mse.json', 'w') as f:
        json.dump(mse_dict, f)  


if __name__ == "__main__":
    get_mae()