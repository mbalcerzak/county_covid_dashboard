from altair.vegalite.v4.api import concat
import streamlit as st
import json
import pandas as pd
import os


@st.cache
def get_locations_json():
    with open("data/sample/locations_sample.json", "r") as f:
       return json.load(f)

@st.cache
def get_true_cases():
    with open("data/sample/county_true_cases_sample.json", "r") as f:
       return json.load(f)

@st.cache
def get_true_cases_prc():
    with open("data/true_cases_prc.json", "r") as f:
       return json.load(f)

@st.cache
def get_predicted_cases(model):
    with open(f"data/sample/model_results/{model}.json", "r") as f:
       return json.load(f)

@st.cache
def get_predicted_cases_prc(model):
    with open(f"data/sample/model_results/{model}_prc.json", "r") as f:
       return json.load(f)

@st.cache
def get_vacc_rates():
    with open("data/vacc_rates_county.json", "r") as f:
       return json.load(f)

@st.cache
def get_population():
    with open("data/populations.json", "r") as f:
       return json.load(f)

@st.cache
def get_models():
    return [x.rstrip('.json') for x in os.listdir('data/sample/model_results') if 'prc' not in x]

@st.cache
def get_mae_mse():
    with open(f'data/mae.json', 'r') as f:
        mae = json.load( f)  
    with open(f'data/mse.json', 'r') as f:
        mse = json.load( f)
    return mae, mse 


def get_county_df(df, county, colname):
    df = df[county]
    dates = list(df)
    cases = df.values()
    return pd.DataFrame(list(zip(dates, cases)), columns=['date',colname])

def get_county_name(x):
    return counties[x]


counties = get_locations_json()
vacc_rates = get_vacc_rates()
models = get_models()
populations = get_population()

# st.sidebar.markdown("[by MAB](https://github.com/mbalcerzak)")
county_selected = st.sidebar.selectbox(
    'Select county FIPS number: ', 
    sorted(counties, key=int), 
    format_func=get_county_name)
model = st.sidebar.selectbox('Select which model would you like to see: ', sorted(models))

county_name = counties[county_selected]

# Nominal cases
data_t = get_true_cases()
data_true = get_county_df(data_t, county_selected, 'True')

data_p = get_predicted_cases(model)
data_pred = get_county_df(data_p, county_selected, 'Predicted')

df_both = pd.merge(left=data_true, right=data_pred, on='date', how='inner')
df_both['date'] = pd.to_datetime(df_both['date'],format='%Y-%m-%d', errors='ignore')
df_both = df_both.rename(columns={'date':'index'}).set_index('index')

# Proportional cases
data_t_prc = get_true_cases_prc()
data_t_prc = get_county_df(data_t_prc, county_selected, 'True')

data_p_prc = get_predicted_cases_prc(model)
data_p_prc = get_county_df(data_p_prc, county_selected, 'Predicted')

df_both_prc = pd.merge(left=data_t_prc, right=data_p_prc, on='date', how='inner')
df_both_prc['date'] = pd.to_datetime(df_both_prc['date'],format='%Y-%m-%d', errors='ignore')
df_both_prc = df_both_prc.rename(columns={'date':'index'}).set_index('index')

st.header(f'{county_name}')
as_prc = st.radio("Data presentation", ('Nominal', 'Per 10 000 inhabitants'))

if as_prc == 'Nominal':
    st.subheader('Predicted and True new COVID cases')
    st.line_chart(df_both)

else:
    st.subheader('Predicted and True new COVID cases relative to the population (per 10 000 people)')
    st.line_chart(df_both_prc)

population = populations[county_selected]
st.write(f"Population: {population}")

st.subheader('Vaccination rates for the area')
st.write(f'Fully vaccinated in {county_name}: {vacc_rates[county_selected]} %')

#  MAEs and MSEs
st.subheader(f'Each model performance for {county_name}')
mae, mse = get_mae_mse()
county_mae, county_mse = mae[county_selected], mse[county_selected]
county_mae = dict(sorted(county_mae.items()))
county_mse = dict(sorted(county_mse.items()))

mae_df = pd.DataFrame(county_mae.items(), columns=['Model name', 'MAE'])
mse_df = pd.DataFrame(county_mse.items(), columns=['Model name', 'MSE'])
mae_mse_df = pd.merge(left=mae_df, right=mse_df, on='Model name', how='inner')

st.dataframe(mae_mse_df)