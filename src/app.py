from altair.vegalite.v4.api import concat
import streamlit as st
import json
import pandas as pd


@st.cache
def get_locations_json():
    with open("data/sample/locations_sample.json", "r") as f:
       return json.load(f)

@st.cache
def get_true_cases():
    with open("data/sample/county_true_cases_sample.json", "r") as f:
       return json.load(f)

@st.cache
def get_predicted_cases():
    with open("data/sample/county_predicted_cases_sample.json", "r") as f:
       return json.load(f)

@st.cache
def get_vacc_rates():
    with open("data/vacc_rates_county.json", "r") as f:
       return json.load(f)

def get_county_df(df, county, colname):
    df = df[county]
    dates = list(df)
    cases = df.values()
    return pd.DataFrame(list(zip(dates, cases)), columns=['date',colname])


counties = get_locations_json()
vacc_rates = get_vacc_rates()

county_selected = st.sidebar.selectbox('Select county FIPS number: ', sorted(counties, key=int))
m = st.sidebar.markdown("[by MAB](https://github.com/mbalcerzak)")
county_name = counties[county_selected]

data_t = get_true_cases()
data_true = get_county_df(data_t, county_selected, 'value_true')

data_p = get_predicted_cases()
data_pred = get_county_df(data_p, county_selected, 'value_pred')

st.header(f'Predicted and True cases: {county_name}')
st.write("Model selected: CEID-Walk")

df_both = pd.merge(left=data_true, right=data_pred, on='date', how='inner')
df_both['date'] = pd.to_datetime(df_both['date'],format='%Y-%m-%d', errors='ignore')
df_both = df_both.rename(columns={'date':'index'}).set_index('index')

st.line_chart(df_both)

st.subheader('Vaccination rates for the area')
st.write(f'Fully vaccinated in {county_name}: {vacc_rates[county_selected]} %')