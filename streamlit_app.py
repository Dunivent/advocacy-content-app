#!/usr/bin/env python
# coding: utf-8

# # Guided Advocacy Content Generator
# **Step 1: Inputs & Setup**

# In[1]:


import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Load data
issues_df = pd.read_csv("Social_Issues_List.csv")
fips_df = pd.read_csv("state_and_county_fips_master.csv")

# Prompt 1: Category selection
print("\nStep 1 – Select a Category")
categories = issues_df['Category'].unique().tolist()
for i, cat in enumerate(categories):
    print(f"{i + 1}. {cat}")
cat_idx = int(input("Enter the number of your choice: ")) - 1
category = categories[cat_idx]

# Prompt 2: Issue selection
filtered = issues_df[issues_df['Category'] == category]['Issue'].tolist()
print(f"\nIssues in {category}:")
for i, issue in enumerate(filtered):
    print(f"{i + 1}. {issue}")
issue = filtered[int(input("Enter the number of your choice: ")) - 1]

# Prompt 3: Focus area
focus_areas = ["Raise Awareness", "Take Action", "Outreach Support"]
print("\nStep 3 – Select a Focus Area")
for i, fa in enumerate(focus_areas):
    print(f"{i + 1}. {fa}")
focus_area = focus_areas[int(input("Enter the number of your choice: ")) - 1]

# Prompt 4: State and county
print("\nStep 4 – Select a State and County")
state_input = input("Enter 2-letter state abbreviation (e.g., NY): ").strip().upper()
available_counties = fips_df[fips_df['state'] == state_input]['name'].unique()
sorted_counties = sorted(available_counties)
for i, name in enumerate(sorted_counties):
    print(f"{i + 1}. {name}")
county_input = sorted_counties[int(input("Enter the number of your county: ")) - 1]

# Prompt 5: Number of statistics
try:
    stat_count = int(input("\nStep 5 – How many statistics would you like to include (1–5)? "))
    if not 1 <= stat_count <= 5:
        raise ValueError
except ValueError:
    print("Invalid input. Defaulting to 3.")
    stat_count = 3

print("\n✅ Inputs captured successfully.")


# # Guided Advocacy Content Generator
# **Step 2: Generate and Display Statistical Statements**

# In[3]:


# Step 2: Prepare only the number of statistics requested for selected issue

statements = []
available_stats = []

# Census data
if 'census_stats' in globals():
    available_stats.extend([
        f"The poverty rate in {county_input} County is {census_stats.get('poverty_rate')}.",
        f"The median household income in {county_input} County is {census_stats.get('median_income')}.",
        f"The unemployment rate in {county_input} County is {census_stats.get('unemployment_rate')} (Census data)."
    ])

# BLS data
if 'bls_stats' in globals():
    available_stats.append(
        f"The unemployment rate in {county_input} County is {bls_stats.get('bls_unemployment_rate')} (BLS data)."
    )

# EPI data
if 'epi_data' in globals():
    available_stats.extend([
        f"Low-wage earners saw a {epi_data['low_wage_growth']} growth in wages.",
        f"The top 1% experienced a {epi_data['top_1_percent_growth']} growth in wages.",
        f"The white-Black wage gap is currently {epi_data['white_black_wage_gap']}."
    ])

# EEOC data
if 'eeoc_summary' in globals():
    eeoc_line = "The top 5 discrimination bases according to the EEOC are: " + ", ".join(eeoc_summary["top_5_discrimination_bases"]) + "."
    available_stats.append(eeoc_line)

# Criminal justice
if 'incarceration_stats' in globals():
    jail_count = incarceration_stats["summary"].get("jail_count")
    jail_rate = incarceration_stats["summary"].get("jail_rate_per_100k")
    available_stats.extend([
        f"There are approximately {jail_count} individuals in jail in {county_input} County.",
        f"The incarceration rate is {jail_rate} per 100,000 people."
    ])

if 'use_of_force_stats' in globals():
    force_stats = use_of_force_stats["summary"]
    available_stats.extend([
        f"Reported use-of-force incidents: {force_stats.get('incidents')}.",
        f"The use-of-force rate is {force_stats.get('rate_per_100k')} per 100,000 residents."
    ])

# Trim to selected number of statistics
statements = available_stats[:stat_count]

# Display selected stats for review
print("📊 The following statistical statement(s) will be used in the next step:")
for i, stat in enumerate(statements, 1):
    print(f"{i}. {stat}")

# Confirm global variable for continuity
globals()['statements'] = statements


# # Guided Advocacy Content Generator
# **Step 3: Content Generation & Review**

# In[6]:


from openai import OpenAI
client = OpenAI()

# Join selected statistical statements
joined_stats = "\n".join(statements)

# Focus-area-specific instruction
focus_instructions = {
    "Raise Awareness": "Write a short policy brief, a social media post, and a concise email to supporters using the following statistics.",
    "Take Action": "Create a social media post that includes a clear call to action and uses the following statistics for urgency.",
    "Outreach Support": "Draft an outreach letter or newsletter message using the following statistics to engage partners and supporters."
}

prompt = f"""
You are writing for a nonprofit focused on advocacy.

Topic: {issue}
Location: {county_input} County, {state_input}
Focus Area: {focus_area}

{focus_instructions[focus_area]}

Statistics:
{joined_stats}

Ensure the tone and format align with the focus area.
"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You generate high-impact advocacy content."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=800
)

generated_content = response.choices[0].message.content

print("✅ Generated Advocacy Content:")
print(generated_content)


# # Guided Advocacy Content Generator
# **Step 4: Schedule Review & Posting Setup (Final Fix)**

# In[9]:


from datetime import datetime, timedelta

# Simulated schedule
mock_schedule = [
    {"title": "Policy Brief on Housing", "scheduled_time": "2024-04-25 10:00 AM"},
    {"title": "Outreach Letter - Health Access", "scheduled_time": "2024-04-26 2:00 PM"},
    {"title": "Social Media Post - Voting Rights", "scheduled_time": "2024-04-27 12:00 PM"},
]

print("📅 Current Scheduled Posts:")
for item in mock_schedule:
    print(f"- {item['title']} at {item['scheduled_time']}")

# Suggest next slot
next_slot = datetime.now() + timedelta(days=1)
suggested_date = next_slot.strftime("%Y-%m-%d")
suggested_time = "10:00 AM"

print(f"\n📌 Suggested Posting Time: {suggested_date} at {suggested_time}")

# Prompt user for scheduling choice
use_suggested = input("Do you want to use the suggested posting time? (yes/no): ").strip().lower()

if use_suggested == "yes":
    scheduled_date = suggested_date
    scheduled_time = suggested_time
    print(f"✅ Scheduled for {scheduled_date} at {scheduled_time}")
else:
    scheduled_date = input("Enter your preferred posting date (YYYY-MM-DD): ").strip()
    scheduled_time = input("Enter your preferred posting time (e.g., 2:30 PM): ").strip()
    print(f"✅ Scheduled for {scheduled_date} at {scheduled_time}")


# # Guided Advocacy Content Generator
# **Step 5: Summary & Internal Email to Leadership**

# In[11]:


# Generate summary of scheduled content
summary = f"""
📢 Advocacy Content Scheduled

- Topic: {issue}
- Location: {county_input}, {state_input}
- Focus Area: {focus_area}
- Scheduled Posting Time: {scheduled_date} at {scheduled_time}
- Key Statistics Used: {stat_count}

The content has been reviewed and approved for release. Please see below for full copy.
"""

# Email content (mock for demonstration)
internal_email = f"""
To: Advocacy & Policy Leadership Team
Subject: Scheduled Advocacy Content – {issue}

Hello Team,

This is a summary of newly approved content for upcoming distribution:

{summary}

Full Content:
{generated_content}

Best,
Automated Advocacy Generator
"""

print("✅ Internal Email to Leadership:")
print(internal_email)


# In[ ]:




