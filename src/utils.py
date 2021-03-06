from collections import defaultdict
import urllib.request
import json 
import pandas as pd
import random


def covid_repo_path():
    with open('config.json','r') as f:
        return json.load(f)


def get_counties_population():
    with open("data/populations.json", "r") as f:
       return json.load(f)


def get_random_counties():
    """Returns a list of counties's FIPS numbers"""
    with open('./data/sample/sample_counties_list.json','r') as f:
        loc_sample = json.load(f)
    return loc_sample


def get_vacc_rates(sample=False):
    url_cdc = "https://covid.cdc.gov/covid-data-tracker/COVIDData/getAjaxData?id=vaccination_county_condensed_data"

    with urllib.request.urlopen(url_cdc) as url:
        data = json.loads(url.read().decode())

    vacc_rates_county = {}

    if sample:
        sample_county_list = get_random_counties()
        vacc_rates_sample = {}
    
    for n, county in enumerate(data["vaccination_county_condensed_data"]):
        print(f"{n}, {county['County']}")
        if county['FIPS'] != 'UNK':
            fips = county['FIPS'].lstrip('0')
            vacc_rates_county[fips] = county['Series_Complete_Pop_Pct']

            if sample:
                if fips in sample_county_list:
                    vacc_rates_sample[fips] = county['Series_Complete_Pop_Pct']

    with open('./data/vacc_rates_county.json', 'w') as f:
        json.dump(vacc_rates_county, f)

    if sample:
        with open('./data/sample/vacc_rates_sample.json', 'w') as f:
            json.dump(vacc_rates_sample, f)


def get_location_names():
    url_loc = "https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-locations/locations.csv"
    loc_dict = {}

    random.seed=42

    df = pd.read_csv(url_loc)
    print(df.head())

    locations = dict(zip(df['location'], df['location_name']))
    
    locations.pop('US')
    counties_keys = [x for x in locations if int(x) > 1000]
    state_keys = [x for x in locations if int(x) < 1000]

    loc_dict = { k.lstrip('0'): f"{locations[k]} ({locations[k[:2]]})" for k in counties_keys }
    print(loc_dict)

    loc_dict_states = { k: f"{locations[k]}" for k in state_keys }

    sample_counties_list = random.sample(loc_dict.keys(), 10)

    with open('./data/locations.json', 'w') as f:
        json.dump(loc_dict, f)

    with open('./data/locations_states.json', 'w') as f:
        json.dump(loc_dict_states, f)

    # with open('./data/sample/sample_counties_list.json', 'w') as f:
    #     json.dump(sample_counties_list, f)


def get_new_county_cases():
    url_true = "https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-truth/truth-Incident%20Cases.csv"

    df = pd.read_csv(url_true)
    print(df.head())

    cases_true = {}

    for location in list(set(df['location'])):
        print(location)
        data = df[df['location'] == location]

        cases_true[location] = dict(zip(data['date'], data['value']))

    with open('./data/counties_true_cases.json', 'w') as f:
        json.dump(cases_true, f)


def select_sample_new_cases():

    with open('data/counties_true_cases.json', 'r') as f:
        all_tue_cases = json.load(f)

    with open('data/sample/sample_counties_list.json', 'r') as f:
        locations = json.load(f) 

    sample_county_cases = {x: all_tue_cases[x] for x in locations}

    with open('data/sample/county_true_cases_sample.json', 'w') as f:
        json.dump(sample_county_cases, f) 


def get_locations_name_sample():

    with open('data/locations.json', 'r') as f:
        locations_all = json.load(f)

    with open('data/sample/sample_counties_list.json', 'r') as f:
        locations = json.load(f) 

    sample_location_names = {x: locations_all[x] for x in locations}

    with open('data/sample/locations_sample.json', 'w') as f:
        json.dump(sample_location_names, f) 


def get_population():
    location_path = f'{covid_repo_path()}/data-locations/locations.csv'
    df = pd.read_csv(location_path)

    locations = df['location'].apply(lambda x: x.lstrip('0'))
    populations = df['population'].apply(lambda x: str(x).rstrip('.0'))
    populations = dict(zip(locations, populations))

    with open('data/populations.json', 'w') as f:
        json.dump(populations, f) 


def get_true_cases_prc():
    """JSON with new cases as a percent of population in each county"""
    with open('data/sample/county_true_cases_sample.json', 'r') as f:
        true_cases = json.load(f)

    populations = get_counties_population()
    print(populations)
    true_cases_prc = defaultdict(dict)

    for county, value in true_cases.items():
        print(county)
        pop = int(populations[county])
        true_cases_prc[county] = {key: (int(value[key])*10000 / pop) for key in value}

    with open('data/true_cases_prc.json', 'w') as f:
        json.dump(true_cases_prc, f) 





if __name__ == "__main__":
    # get_population()
    get_true_cases_prc()
