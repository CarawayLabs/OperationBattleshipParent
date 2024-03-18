"""
This Python Script is a WebApp that displays data which is driven by Streamlit. 

We will be exploring the data about AI jobs available to us. We want to learn more about these things:
- Salary ranges
- Where are they located
- Posting Data
- Where are they located
- Top job unique job titles by posting volume   



"""

#CSV File is created from the SQL in this file:
# ...\OperationBattleshipParent\Database\jobsWithCompanyName.sql

import streamlit as st
import pandas as pd
import sys
import logging
import os
from dotenv import load_dotenv
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Get the directory of the script being run:
current_script_path = os.path.abspath(__file__)

# Get the parent directory of the current script:
parent_directory = os.path.dirname(os.path.dirname(current_script_path))

# Add the parent directory to the sys.path:
if parent_directory not in sys.path:
    sys.path.append(parent_directory)

from CommonUtilities.JobPostingDao import JobPostingDao




import psycopg2

load_dotenv('.env')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

st.set_page_config(page_title='AI Jobs Analytics', layout='wide')  # Optional: Set some config for the Streamlit app

def showWeeklyTrendJobPostings(df):
    # 1. Filter the DataFrame
    ai_jobs = df[df['is_ai'] == True]

    # 2. Ensure job_posting_date is a datetime
    ai_jobs['job_posting_date'] = pd.to_datetime(ai_jobs['job_posting_date'])

    # 3. Resample and count job postings per week
    weekly_counts = ai_jobs.resample('W', on='job_posting_date').size().reset_index(name='count')

    # 4. Plotting with Plotly
    fig = px.line(weekly_counts, x='job_posting_date', y='count', title='Weekly AI Job Postings Trend', labels={'count': 'Number of Job Postings', 'job_posting_date': 'Week'})
    fig.update_traces(mode='lines+markers')  # Optional: Add markers to the line
    fig.update_layout(xaxis_title='Week', yaxis_title='Number of Job Postings', xaxis_tickangle=-45)
    fig.update_xaxes(nticks=20)  # Optional: Adjust the number of ticks/labels on the x-axis for readability

    # Use Streamlit's function to display the plot
    st.plotly_chart(fig, use_container_width=True)

    return 

def displayTablePercentOfAiJobs(df):
    # Show a table to tell the percent of non-null is_ai records that is true vs fale
    # We want to print a table view where one columne is_ai = false and other column is_ai = true
    #The values will be the percent of jobs that are ai vs are not ai 

    return

def pieChartOfPmVsAi(df):
    #Show a pie chart of AI PM Jobs vs Product Manager Jobs

    return 

def tableOfAiJobs(df): 
    #show a table of AI Jobs sorted by highest midpoint first

    return 


def main(args):

    st.title('AI Jobs Analytics')
    
    #We use this SQL Select Statement to generate this CSV File. I haven't figured out why I cannot connect to the Digital Ocean PostGres DB. 
    # ...\OperationBattleshipParent\Database\jobsWithCompanyName.sql
    absFilePath = "C:\\Users\\caraw\\OneDrive\\Documents\\PythonProjects\\OperationBattleshipParent\\OperationBattleshipFrontEndStreamlit\\resources\\Feb4.csv"
    jobs = pd.read_csv(absFilePath)    
    
    #Show a weekly trend of AI Jobs being posted
    showWeeklyTrendJobPostings(jobs)

    
    #Show a table to tell the percent of non-null is_ai records that is true vs fale
    displayTablePercentOfAiJobs(jobs)

    #Show a pie chart of AI PM Jobs vs Product Manager Jobs
    pieChartOfPmVsAi(jobs)

    #show a table of AI Jobs sorted by highest midpoint first
    tableOfAiJobs(jobs)



    return

# This ensures the app doesn't run on import if this script is imported as a module elsewhere
if __name__ == "__main__":

    args = {"name": sys.argv[1]} if len(sys.argv) > 1 else {}
    
    main(args)