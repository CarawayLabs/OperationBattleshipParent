"""
This Python Script is a WebApp that displays data which is driven by Streamlit. 

We will be exploring the data about jobs available to us. 

In order to get that data, we will need to query the JobPostingDao class and call the method. "getAllJobs()"

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

st.set_page_config(page_title='Market Analytics', layout='wide')  # Optional: Set some config for the Streamlit app



def showBoxplotWithObservations(df):

    df_filtered = df[df['salary_midpoint'].notnull()]

    # Step 2: Setup Seaborn and Matplotlib for Streamlit
    sns.set(style="whitegrid")

    # Step 3: Create the Horizontal Boxplot with Observations
    plt.figure(figsize=(10, 6))
    ax = sns.boxplot(x=df_filtered['salary_midpoint'], orient="h", color="lightblue", fliersize=0)  # fliersize=0 hides the outliers
    sns.stripplot(x=df_filtered['salary_midpoint'], orient="h", color='darkblue', alpha=0.5)  # Add stripplot to overlay the data points

    # Customizations - optional (you can add titles, labels, or change the aesthetics)
    ax.set_title('Salary Midpoint Distribution with Observations')
    ax.set_xlabel('Salary Midpoint')
    ax.set_ylabel('Jobs')

    # Step 4: Display the Plot in Streamlit
    st.pyplot(plt)
    
    return 

def showViolinPlotOfSalaryMidpoint(df):
    df_filtered = df[df['salary_midpoint'].notnull()]

    # Step 2: Setup Seaborn and Matplotlib for Streamlit
    sns.set(style="whitegrid")

    # Step 3: Create the Violin Plot
    plt.figure(figsize=(10, 6))
    ax = sns.violinplot(x=df_filtered['salary_midpoint'])

    # Customizations - optional (you can add titles, labels, or change the aesthetics)
    ax.set_title('Distribution of Salary Midpoints')
    ax.set_xlabel('Salary Midpoint')
    ax.set_ylabel('Density')

    # Step 4: Display the Plot in Streamlit
    st.pyplot(plt)

    return 




def showCountOfJobsByCompanyName(df):

    company_name_counts = df.groupby('company_name').size().reset_index(name='counts')
    company_name_counts = company_name_counts.sort_values('counts', ascending=False)
    company_name_counts = company_name_counts.reset_index(drop=True)
    company_name_counts.columns = ['Company Name', 'Number of Postings']
    st.table(company_name_counts)

    return 

def showCountOfJobsByTitle(df):
    # Step 1: Aggregate data
    job_title_counts = df.groupby('job_title').size().reset_index(name='counts')

    # Step 2: Sort values (Optional)
    job_title_counts = job_title_counts.sort_values('counts', ascending=False)

    # Step 3: Reset index (if needed after sorting)
    job_title_counts = job_title_counts.reset_index(drop=True)

    # Step 4: Rename columns
    job_title_counts.columns = ['Job Title', 'Number of Postings']

    # Step 5: Display table in Streamlit
    st.table(job_title_counts)

    return 

def showJobTitlesWithSpecifiedRange(df, low=145000, high=200000):
    """
    Filters the dataframe for records that have value for the salary_midpoint column that is between the low and high value from the function args. 
    Default value for low when not provided us 145,000
    Default value for low when not provided us 200,000

    Once the df has been filter, we call showCountOfJobsByTitle(df) and it will display the results. 

    """
    filtered_df = df[(df['salary_midpoint'] >= low) & (df['salary_midpoint'] <= high)]
    
    st.write("Job Titles where salary is greater than {low} and less than {high}")
    showCountOfJobsByTitle(filtered_df)

    return

def showHistogram(df):
    filtered_df = df.dropna(subset=['salary_midpoint'])
    plt.figure(figsize=(10,6))  # Adjusts the size of the histogram
    plt.hist(filtered_df['salary_midpoint'], bins=30, color='blue', edgecolor='black')
    plt.title('Distribution of Salary Midpoints')  # Adds a title to your histogram
    plt.xlabel('Salary Midpoint')  # Adds a label to the x-axis
    plt.ylabel('Frequency')  # Adds a label to the y-axis
    plt.grid(True)  # Adds a grid to the background

    # Use Streamlit's method to display the plot
    st.pyplot(plt)


    return

def salaryMidpointStats(df):
        # Ensure there are no missing values in the 'salary_midpoint' column
    filtered_df = df['salary_midpoint'].dropna()

    # Calculate statistics
    mean_value = filtered_df.mean()
    median_value = filtered_df.median()
    std_dev = filtered_df.std()
    min_value = filtered_df.min()
    max_value = filtered_df.max()
    quantiles = filtered_df.quantile([0.25, 0.5, 0.75])
    count = filtered_df.count()
    total_sum = filtered_df.sum()

    # Display statistics using Streamlit
    st.write("### Salary Midpoint Statistics")
    st.write("Count:", count)
    st.write("Sum:", total_sum)
    st.write("Mean:", mean_value)
    st.write("Median:", median_value)
    st.write("Standard Deviation:", std_dev)
    st.write("Minimum:", min_value)
    st.write("Maximum:", max_value)
    st.write("25th Percentile:", quantiles[0.25])
    st.write("50th Percentile (Median):", quantiles[0.5])
    st.write("75th Percentile:", quantiles[0.75])

    # Optional: Display Histogram
    st.write("### Histogram of Salary Midpoints")
    fig, ax = plt.subplots()
    filtered_df.hist(ax=ax, bins=30, color='blue', edgecolor='black')
    ax.set_title('Distribution of Salary Midpoints')
    ax.set_xlabel('Salary Midpoint')
    ax.set_ylabel('Frequency')
    st.pyplot(fig)

    return

def main(args):

    st.title('Market Analytics')
    
   
    absFilePath = "C:\\Users\\caraw\\OneDrive\\Documents\\PythonProjects\\OperationBattleshipParent\\OperationBattleshipFrontEndStreamlit\\resources\\Feb4.csv"
    jobs = pd.read_csv(absFilePath)    

#    st.write(jobs)
    st.write(jobs.shape)
    
    # Display the columns of the DataFrame
    st.write('Columns in the DataFrame:')
    st.write(jobs.columns.tolist())

    # Display the columns of the DataFrame
    st.write('Describe the DataFrame:')
    st.write(jobs.describe())
    
    st.write('DataFrame Head:')
    st.write(jobs.head())

    salaryMidpointStats(jobs)

    showViolinPlotOfSalaryMidpoint(jobs)

    showBoxplotWithObservations(jobs)

    showHistogram(jobs)

    showJobTitlesWithSpecifiedRange(jobs, 145000, 200000)

    #Do the jobs change when we have is_ai = true?

    ai_jobs = jobs[jobs['is_ai'] == True] #Remove all the records from the dataframw where the column "is_ai" = false. 

    
    salaryMidpointStats(ai_jobs)
    showViolinPlotOfSalaryMidpoint(ai_jobs)
    showBoxplotWithObservations(ai_jobs)
    showHistogram(ai_jobs)
    showJobTitlesWithSpecifiedRange(ai_jobs, 145000, 200000)




    
 #   showCountOfJobsByTitle(jobs)

#    showCountOfJobsByCompanyName(jobs)
    
    return

# This ensures the app doesn't run on import if this script is imported as a module elsewhere
if __name__ == "__main__":
    # Convert command line arguments to a dictionary or any suitable format
    args = {"name": sys.argv[1]} if len(sys.argv) > 1 else {}
    
    main(args)