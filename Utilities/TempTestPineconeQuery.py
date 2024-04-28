
import logging
import numpy as np
from datetime import datetime
import sys
import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import json


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




def main():

    #Important Variables for Pinecone:
    pineconeApiKey = os.getenv("PINECONE_API_KEY")
    indexName = "job-postings"

    fullJobNamespace = "full-posting-description"
    shortJobNamespace = "short-job-description"
    jobTitleNamespace = "job-title"

    #Set up the index
    pineConeDatabaseCaller = PineConeDatabaseCaller(pineconeApiKey)

    #Get a job
    jobPostingDao = JobPostingDao()
    jobs = jobPostingDao.getAllProductManagerJobs()
    jobs = jobs.head(1)


    #Embed the full posting description
    embeddedFullPostingDescriptionTextAndMetaData = embedTextAndAddMetadata(jobs, "full_posting_description")

    print(embeddedFullPostingDescriptionTextAndMetaData)
    print("\n---\n")
#    print(embeddedFullPostingDescriptionTextAndMetaData[0])

    embedding = embeddedFullPostingDescriptionTextAndMetaData[list(embeddedFullPostingDescriptionTextAndMetaData.keys())[0]]['embedding']
    print(embedding)
        
    queriedVectorResponse = pineConeDatabaseCaller.query(embeddedFullPostingDescriptionTextAndMetaData[list(embeddedFullPostingDescriptionTextAndMetaData.keys())[0]]['embedding'], 10, indexName, fullJobNamespace, 45)
    # Save the quried vector response to a file called full_posting_description_query_response
    file_path = 'full_posting_description_query_response.json'
    with open(file_path, 'w') as file:
        json.dump(queriedVectorResponse, file, indent=4)

    
    #Embed Job Titles
    embeddedJobTitleTextAndMetaData = embedTextAndAddMetadata(jobs, "job_title")
    queriedVectorResponse = pineConeDatabaseCaller.query(embeddedJobTitleTextAndMetaData[0]["embedding"], 10, indexName, jobTitleNamespace, 45)        
    file_path = 'job_title_query_response.json'
    with open(file_path, 'w') as file:
        json.dump(queriedVectorResponse, file, indent=4)

    
    #Embed Short Job Description
    embeddedShortJobDescriptionTextAndMetaData = embedTextAndAddMetadata(jobs, "job_description")
    queriedVectorResponse = pineConeDatabaseCaller.query(embeddedShortJobDescriptionTextAndMetaData[0]["embedding"], 10, indexName, shortJobNamespace, 45)        
    file_path = 'short_description_query_response.json'
    with open(file_path, 'w') as file:
        json.dump(queriedVectorResponse, file, indent=4)
    
 
    logging.info("Completed processing all jobs.")  

    return 


def embedTextAndAddMetadata(jobsDataFrame, columnToEmbed):
    """
    Args: 
    - jobsDataFrame: A pandas dataframe that contains several columns. This function needs
        - job_posting_id (UUID)
        - columnToEmbed (String): The column title from the jobsDataFrame that contains the text to be embedded.
    
    Return value: 
        Intended to be a collection of Job Posting IDs (UUID) and embeddings to represent the text of a job description.
        Will also contain metadata for each job posting.
    """ 
    # Assuming jobsDataFrame is not empty and has only one row
    row = jobsDataFrame.iloc[0]
    row = cleanAllValues(row)

    textToEmbed = row[columnToEmbed]
    nomicAICaller = NomicAICaller()
    embedding = nomicAICaller.embedDocument(textToEmbed)
    
    job_posting_id = row['job_posting_id']
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

    data = {job_posting_id: {'embedding': embedding, 'metadata': metadata}}
    
    return data


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

    job_posting["job_posting_date"] = daysSinceEpoch(job_posting["job_posting_date"])

    return job_posting

def daysSinceEpoch(job_posting_date, epoch_str='1970-01-01'):
    date = datetime.strptime(str(job_posting_date), '%Y-%m-%d')
    epoch = datetime.strptime(epoch_str, '%Y-%m-%d')
    delta = date - epoch
    return delta.days

if __name__ == "__main__":
    logging.info(f"Script to test the new Pinecone query has started.")

    main()