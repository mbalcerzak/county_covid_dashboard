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


counties = get_locations_json()
vacc_rates = get_vacc_rates()

county_selected = st.sidebar.selectbox('Select county FIPS number: ', sorted(counties, key=int))

data = get_true_cases()
data = data[county_selected]
dates = list(data)
cases = data.values()

df = pd.DataFrame(list(zip(dates, cases)), columns=['date','value'])
df['date'] = pd.to_datetime(df['date'],format='%Y-%m-%d', errors='ignore')
df = df.rename(columns={'date':'index'}).set_index('index')

# date_range = st.slider('Select a date range', min(dates), max(dates), (min(dates), max(dates)))

county_name = counties[county_selected]

st.title('Recorded new cases')
st.header(f'Actual cases: {county_name}')

st.line_chart(df)

data_pred = get_predicted_cases()
data_pred = data_pred[county_selected]
dates_pred = list(data_pred)
cases_pred = data_pred.values()

df_pred = pd.DataFrame(list(zip(dates_pred, cases_pred)), columns=['date','value'])
df_pred['date'] = pd.to_datetime(df_pred['date'],format='%Y-%m-%d', errors='ignore')
df_pred = df_pred.rename(columns={'date':'index'}).set_index('index')

st.header('Predicted cases (model: CEID-Walk)')
st.line_chart(df_pred)

st.subheader('Vaccination rates for the area')
st.write(f'Fully vaccinated in {county_name}: {vacc_rates[county_selected]} %')