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
def get_vacc_rates():
    with open("data/vacc_rates_county.json", "r") as f:
       return json.load(f)

counties = get_locations_json()
vacc_rates = get_vacc_rates()

county_selected = st.sidebar.selectbox('Predicted and actual new COVID cases in ', counties)

data = get_true_cases()
data = data[county_selected]
dates = list(data)
cases = data.values()

df = pd.DataFrame(list(zip(dates, cases)), columns=['date','value'])
df['date'] = pd.to_datetime(df['date'],format='%Y-%m-%d', errors='ignore')
df = df.rename(columns={'date':'index'}).set_index('index')

# date_range = st.slider('Select a date range', min(dates), max(dates), (min(dates), max(dates)))

st.title('Recorded new cases')
st.header(f'{counties[county_selected]}')

st.line_chart(df)

st.subheader('Vaccination rates for the area')
st.write(f'Fully vaccinated as % of population in that county: {vacc_rates[county_selected]}')