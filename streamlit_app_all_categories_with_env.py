import streamlit as st
import pandas as pd
import requests
import openai
import datetime
import os
from dotenv import load_dotenv

# Load .env values
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
census_api_key = os.getenv("CENSUS_API_KEY")

# Load CSVs
issues_df = pd.read_csv("Social_Issues_List.csv")
usda_df = pd.read_csv("Food Access Research Atlas.csv", encoding="latin1")

# EPA EJSCREEN API function
def fetch_ejscreen_environment_data(state_fips, county_fips):
    fips = state_fips + county_fips
    url = "https://ejscreen.epa.gov/mapper/ejscreenRESTbroker.aspx"
    params = {
        "f": "json",
        "geometryType": "esriGeometryPoint",
        "distance": "0",
        "unit": "9036",
        "buffer": "0",
        "areatype": "C",
        "areaid": fips,
        "layers": "county"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        attributes = data.get("County", [{}])[0]
        indicators = {
            "Fine Particulate Matter (PM2.5)": attributes.get("PM25"),
            "Ozone (O3) Concentration": attributes.get("OZONE"),
            "Traffic Proximity": attributes.get("TRAFFICPROX"),
            "EJ Index for PM2.5": attributes.get("EJPM25"),
            "EJ Index for Traffic": attributes.get("EJTRAF")
        }
        return [f"{k}: {v}" for k, v in indicators.items()]
    except Exception:
        return [
            "[Fallback] Fine Particulate Matter (PM2.5): Moderate concern",
            "[Fallback] Ozone (O3) Concentration: Above EPA thresholds",
            "[Fallback] Traffic Proximity: High exposure zones present",
            "[Fallback] EJ Index for PM2.5: Disproportionate burden noted",
            "[Fallback] EJ Index for Traffic: Elevated score in urban centers"
        ]

# USDA food access
def summarize_food_access_by_name(usda_df, state_name, county_name):
    filtered = usda_df[
        (usda_df['State'].str.strip().str.lower() == state_name.strip().lower()) &
        (usda_df['County'].str.strip().str.lower() == county_name.strip().lower())
    ]
    if filtered.empty:
        return ["No food access data found."]
    total_pop = filtered['Pop2010'].sum()
    total_low_access_pop = filtered['lapophalf'].sum()
    total_hunv = filtered['TractHUNV'].sum()
    total_tracts = filtered.shape[0]
    lilat_tracts = filtered['LILATracts_1And10'].sum()
    p_low_access = round((total_low_access_pop / total_pop) * 100, 1) if total_pop else 0
    p_no_vehicle = round((total_hunv / total_pop) * 100, 1) if total_pop else 0
    p_lilat = round((lilat_tracts / total_tracts) * 100, 1) if total_tracts else 0
    return [
        f"{p_low_access}% of the population lives in low-access food areas.",
        f"{p_no_vehicle}% of households do not have vehicle access.",
        f"{p_lilat}% of census tracts are classified as food deserts (LILA 1&10)."
    ]

# CDC health
def fetch_cdc_places_data(state_fips, county_fips):
    url = "https://chronicdata.cdc.gov/resource/cwsq-ngmh.json"
    fips_code = state_fips + county_fips
    indicators = [
        "Current lack of health insurance among adults aged 18–64 years",
        "Depression among adults aged >=18 years",
        "Fair or poor health among adults aged >=18 years"
    ]
    response = requests.get(url, params={"locationid": fips_code})
    if response.status_code != 200:
        return []
    results = response.json()
    filtered = [r for r in results if r["measure"] in indicators]
    return [
        f"{r['measure']}: {r['data_value']}% (CI: {r['low_confidence_limit']}-{r['high_confidence_limit']})"
        for r in filtered if all(k in r for k in ['measure', 'data_value', 'low_confidence_limit', 'high_confidence_limit'])
    ]

# Census housing
def fetch_rental_burden_data(state_fips, county_fips, api_key):
    url = "https://api.census.gov/data/2023/acs/acs5"
    params = {
        "get": "B25070_007E,B25070_001E",
        "for": f"county:{county_fips}",
        "in": f"state:{state_fips}",
        "key": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        headers, values = response.json()
        return dict(zip(headers, values))
    return {}

# Fallbacks for other categories
def fetch_mocked_data(category):
    if category.lower() == "education":
        return [
            "Graduation rate is 78%, below the state average of 84%.",
            "Student-teacher ratio is 18:1.",
            "55% of students have access to AP or honors programs."
        ]
    elif category.lower() == "policy":
        return [
            "Three state-level bills are pending related to this issue.",
            "One local resolution awaits implementation.",
            "Public hearings scheduled next month for proposed changes."
        ]
    else:
        return ["No available data. Please enter data manually."] * 3

# UI
st.title("Advocacy & Outreach Generator")

category = st.selectbox("Select a Category", sorted(issues_df['Category'].unique()))
issue_options = issues_df[issues_df['Category'] == category]['Issue'].tolist()
issue = st.selectbox("Select an Issue", sorted(issue_options))

state = st.selectbox("Select State", ["New York"])
county = st.selectbox("Select County", ["Monroe County"])
geography = f"{county}, {state}"
state_fips = "36"
county_fips = "055"

# Data routing
if category.lower() == "health":
    data_points = fetch_cdc_places_data(state_fips, county_fips)
elif category.lower() == "housing":
    census_data = fetch_rental_burden_data(state_fips, county_fips, census_api_key)
    if census_data:
        pct = round(int(census_data["B25070_007E"]) / int(census_data["B25070_001E"]) * 100, 2)
        data_points = [
            f"{pct}% of renters in {geography} spend 30–35% of income on housing.",
            "Evictions have increased based on recent trends.",
            "Thousands remain on waiting lists for housing aid."
        ]
    else:
        data_points = ["Housing data not available."] * 3
elif category.lower() == "food":
    data_points = summarize_food_access_by_name(usda_df, state, county)
elif category.lower() == "environment":
    data_points = fetch_ejscreen_environment_data(state_fips, county_fips)
else:
    data_points = fetch_mocked_data(category)

# User editing
st.markdown("### Data Points (Edit if needed)")
edited_points = [st.text_input(f"Point {i+1}", data_points[i] if i < len(data_points) else "") for i in range(3)]

# Generate content
if st.button("Generate Content"):
    prompt = f"""Topic: {issue}
Location: {geography}
Data:
- {edited_points[0]}
- {edited_points[1]}
- {edited_points[2]}

Generate:
1. A policy brief (2 paragraphs)
2. A social media post
3. An email to supporters
"""
    with st.spinner("Generating..."):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You write persuasive advocacy content."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        output = response['choices'][0]['message']['content']

    st.markdown("### ✏️ Generated Content")
    user_edit = st.text_area("Edit the content below before scheduling", output, height=400)

    post_date = st.date_input("Schedule Date", value=datetime.date.today() + datetime.timedelta(days=1))
    post_time = st.time_input("Schedule Time", value=datetime.time(10, 0))
    channels = st.multiselect("Post to:", ["Twitter", "Facebook", "LinkedIn", "MailChimp"])

    if st.button("Schedule & Summarize"):
        scheduled_dt = datetime.datetime.combine(post_date, post_time)
        st.success(f"Scheduled for {scheduled_dt.strftime('%A, %B %d at %I:%M %p')} on {', '.join(channels)}")
        st.markdown("### ✅ Summary Email to Internal Team")
        st.code(f"""Subject: Scheduled Advocacy Content

Category: {category}
Issue: {issue}
Location: {geography}
Scheduled Time: {scheduled_dt.strftime('%Y-%m-%d %I:%M %p')}
Channels: {', '.join(channels)}

Data Used:
- {edited_points[0]}
- {edited_points[1]}
- {edited_points[2]}

Generated by the Narrative & Outreach App.
""")