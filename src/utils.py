import urllib.request
import json 
import pandas as pd
import random


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

    df = pd.read_csv(url_loc)
    print(df.head())

    locations = dict(zip(df['location'], df['location_name']))
    
    locations.pop('US')
    counties_keys = [x for x in locations if int(x) > 1000]
    state_keys = [x for x in locations if int(x) < 1000]

    loc_dict = { k.lstrip('0'): f"{locations[k]} ({locations[k[:2]]})" for k in counties_keys }
    print(loc_dict)

    loc_dict_states = { k: f"{locations[k]}" for k in state_keys }

    locations_sample = random.sample(loc_dict.keys(), 10)

    with open('./data/locations.json', 'w') as f:
        json.dump(loc_dict, f)

    with open('./data/locations_states.json', 'w') as f:
        json.dump(loc_dict_states, f)

    with open('./data/sample/locations_sample.json', 'w') as f:
        json.dump(locations_sample, f)


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


if __name__ == "__main__":
    get_location_names()
