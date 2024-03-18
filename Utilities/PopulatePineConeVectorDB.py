"""
General flow of script: 
1: Ensure the Pinecone Index exists. 
2: Get the list of jobs as a dataframe. 
3: Call Nomic.AI and embed the Full Posting Description of the job. 
4: Send the data element to Pinecone and persist into the vector DB. 
    - job_posting_id (GUUID)
    - full_posting_description (text -> embedding)
    Metadata for Job
        - is_ai (Boolean)
        - salary_midpoint (INT)
        - job_category (String)
"""

import logging
import numpy as np
from datetime import datetime
import sys
import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

log_file_path = os.path.join(Path(__file__).parent.absolute(), 'logfile.log')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s',
                    filename=log_file_path,
                    filemode='w')

# Get the directory of the script being run:
current_script_path = os.path.abspath(__file__)

# Get the parent directory of the current script:
parent_directory = os.path.dirname(os.path.dirname(current_script_path))

# Add the parent directory to the sys.path:
if parent_directory not in sys.path:
    sys.path.append(parent_directory)

from CommonUtilities.PineConeDatabaseCaller import PineConeDatabaseCaller
from CommonUtilities.JobPostingDao import JobPostingDao
from CommonUtilities.NomicAICaller import NomicAICaller

load_dotenv('.env')



def cleanAllValues(job_posting):

    """
    The job_posting arguement is a row from a pandas dataframe and we want to update if any of these values are null. 
    The text below lists the variable name and also the value we will assign to if it is null. 
    "is_ai' = false (boolean)
    'job_posting_date' = current date, as written in this format: (2023-12-01)
    'salary_low' = -1 (int)
    'salary_midpoint' = -1 (int)
    'salary_high' = -1 (int)
    'is_genai' = false (boolean)
    'work_location_type' = remote (string)
    'job_category' = unknown (string)
    """
    # Define default values for each specified column
    defaults = {
        'is_ai': False,
        'job_posting_date': datetime.now(),  # Current date in 'YYYY-MM-DD' format
        'salary_low': -1,
        'salary_midpoint': -1,
        'salary_high': -1,
        'is_genai': False,
        'work_location_type': 'remote',
        'job_category': 'unknown',
        'job_description': 'Empty Text'
    }
    
    # Iterate through the defaults dictionary and update job_posting if value is NaN, null, or empty
    for column, default_value in defaults.items():
        if pd.isna(job_posting[column]) or job_posting[column] == '':
            logging.debug(f"Value is null on job record. Updating for column name: {column}")
            job_posting[column] = default_value
        elif column == 'job_posting_date':  # Ensure job_posting_date is always a datetime object
            # Convert to datetime if not null or already a datetime object
            if not isinstance(job_posting[column], datetime):
                try:
                    job_posting[column] = pd.to_datetime(job_posting[column]).date()
                except ValueError:
                    logging.error(f"Invalid date format in 'job_posting_date' for job record. Setting to default current date.")
                    job_posting[column] = defaults['job_posting_date'].date()
            else:
                job_posting[column] = job_posting[column].date()  # Ensure format is date only, no time

    return job_posting

def embedTextAndAddMetadata(jobsDataFrame, columnToEmbed):
    """
    Args: 
    - jobsDataframe: A pandas dataframe that contains several columns. This function needs
        - job_posting_id (UUID)
        - columnToEmbed (String): The column title from the jobsDataFrame that contains the text to be embedded.
    
    Return value: 
        Intended to be a collection of Job Posting IDs (UUID) and embeddings to represent the text of a job description.
        Will also contain metadata for each job posting.
    """ 
    data = {}
    nomicAICaller = NomicAICaller()
    for index, row in jobsDataFrame.iterrows():
        row = cleanAllValues(row)

        textToEmbed = row[columnToEmbed]
        embedding = nomicAICaller.embedDocument(textToEmbed)
        
        job_posting_id = row["job_posting_id"]
        metadata = {
            'is_ai': row.get('is_ai', None),
            'is_genai': row.get('is_genai', None),
            'salary_low': row.get('salary_low', None),
            'salary_midpoint': row.get('salary_midpoint', None),
            'salary_high': row.get('salary_high', None),
            'job_category': row.get('job_category', None),
            'job_posting_date': row.get('job_posting_date', None),
            'work_location_type': row.get('work_location_type', None)
        }
        data[job_posting_id] = {'embedding': embedding, 'metadata': metadata}
    
    return data



def getAllJobsToEmbed():
    """
    Our Job Collection Data Pipeline gets a lot of different jobs. 
    In order to save on cost and optimize any results that are returned for me in the job recomendation engine, I've decided to select only a subset of jobs contained in the DB. 
    - Jobs with these categories:
        -Product
        -Data Science
    - There are some jobs that have an unknown category or maybe even were mis-categoriezed, therefore, we will have a slightly wider net also. 
        -Jobs that contain these strings in the job title:
            - AI
            - Prodct
    """

    jobPostingDao = JobPostingDao()
    jobs = jobPostingDao.getAllProductManagerJobs()

    aiOrProductJobs = jobPostingDao.getAllDataScienceOrProductCategorizedJobs()

    # Combine these two dataframes and return the superset
    combined_jobs = pd.concat([jobs, aiOrProductJobs])

    # Drop duplicate rows based on 'job_posting_id', keeping the first occurrence
    superset_jobs = combined_jobs.drop_duplicates(subset='job_posting_id', keep='first')

    return superset_jobs

def main():

    #Important Variables for Pinecone:
    pineconeApiKey = os.getenv("PINECONE_API_KEY")
    indexName = "job-postings" 
    
    #Set up the index
    pineConeDatabaseCaller = PineConeDatabaseCaller(pineconeApiKey)
    pineConeDatabaseCaller.createIndexIfDoesntExist(indexName)
    

    all_jobs = getAllJobsToEmbed()

    while not all_jobs.empty:

        jobs = all_jobs.head(5)

        logging.info(f"Total jobs in all_jobs: {all_jobs.shape[0]}")

        #Embed the full posting description
        embeddedFullPostingDescriptionTextAndMetaData = embedTextAndAddMetadata(jobs, "full_posting_description")        
        upsertEmbeddingsResponse = pineConeDatabaseCaller.upsertEmbeddings(indexName, "full-posting-description", embeddedFullPostingDescriptionTextAndMetaData)
        
        #Embed Job Titles
        embeddedJobTitleTextAndMetaData = embedTextAndAddMetadata(jobs, "job_title")        
        upsertEmbeddingsResponse = pineConeDatabaseCaller.upsertEmbeddings(indexName, "job-title", embeddedJobTitleTextAndMetaData)

        #Embed Short Job Description
        embeddedShortJobDescriptionTextAndMetaData = embedTextAndAddMetadata(jobs, "job_description")        
        upsertEmbeddingsResponse = pineConeDatabaseCaller.upsertEmbeddings(indexName, "short-job-description", embeddedShortJobDescriptionTextAndMetaData)

        all_jobs = all_jobs.iloc[5:]
    
    logging.info("Completed processing all jobs.")  

    return 


if __name__ == "__main__":
    logging.info(f"Script to populate the Pinecone Vector DB has started.")
    main()