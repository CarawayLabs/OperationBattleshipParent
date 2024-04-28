"""
TODO: Can I make this more efficient? I wonder if I download the list of Jobs that exist and I use that in the doesJobExist() instead of calling the DB each time? This should reduce the total calls to the DB and accelerate the time required for this script to execute. 

TODO: Place the logs into a separate file. 

TODO: Update the log level to the correct level. 

"""


"""
Script Overview:
This script is designed for parsing job report data retrieved from the Apify Actor and manages the lifecycle of job data from raw collection to processed records. 
It operates by reading job data from the 'RawCollections' folder, parsing each job's details, and applying logic for job insertion, updating, or skipping based on its presence in the database.

Operational Flow:
1. The script enumerates all JSON files in the 'RawCollections' directory.
2. Each file, representing a batch of job records, is opened and its content is loaded into a pandas DataFrame named 'apifyJobsReport'.
3. It iteratively processes each job record using 'processJobRecord(individualJobRecord)', which handles the logic of insertion or updating records in the database.
4. After processing all job records in the file, the script moves the original raw data file to the 'ProcessedCollections' folder for archiving.

Directory Structure:
- Script Location: C:\\Users\\caraw\\OneDrive\\Documents\\PythonProjects\\OperationBattleship\\python\\JobPostingProcessor.py
- Raw Collections Directory: C:\\Users\\caraw\\OneDrive\\Documents\\PythonProjects\\OperationBattleship\\RawCollections
- Processed Collections Directory: C:\\Users\\caraw\\OneDrive\\Documents\\PythonProjects\\OperationBattleship\\ProcessedCollections

Notes:
- Ensure the RawCollections directory contains only relevant JSON files before running this script.
- Verify database connectivity and schema compatibility for seamless data insertion and updating.
- Review and handle any exceptions or errors during the file and data processing to maintain data integrity and script stability.
"""

import random
import string
import datetime
import uuid
import time
import sys
import logging
import pandas as pd
import json
import shutil
from dotenv import load_dotenv
from datetime import datetime
import os

# Get the directory of the script being run:
current_script_path = os.path.abspath(__file__)

# Get the parent directory of the current script:
parent_directory = os.path.dirname(os.path.dirname(current_script_path))

# Add the parent directory to the sys.path:
if parent_directory not in sys.path:
    sys.path.append(parent_directory)

from CommonUtilities.JobPostingDao import JobPostingDao
from CommonUtilities.CompanyDao import CompanyDao
from CommonUtilities.GeographyHelper import GeographyHelper

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#Global Variable to help track failed Jobs. 
failedJobsCount = 0
failedJobTitles = []


#This function removes the '?' character from the job url. 
def remove_query_parameters(url):
    # Split the URL at the '?' character
    base_url = url.split('?')[0]
    return base_url


def getLinkedInJobRecordId(jobUrl):
    """
    Extracts the unique record ID from a LinkedIn job posting URL.

    The function takes a LinkedIn job posting URL as input and parses it to extract the job record ID, typically found as the last part of the URL. The ID is used to uniquely identify the job posting. The URL usually follows a standard pattern where the ID is appended at the end, after the last dash ('-') and before any query parameters or additional slashes.

    Args:
        jobUrl (str): The complete URL of a LinkedIn job posting.

    Returns:
        str: The extracted unique job record ID from the provided LinkedIn job URL.

    Note:
        LinkedIn job URLs are expected to have a consistent structure where the job ID is delineated by dashes. Any deviations in URL structure may affect the ID extraction accuracy.
    """
    # Split the URL by the dash character
    parts = jobUrl.split('-')
    
    # The last part of the URL, after the last dash, is the ID
    # Further split by any slashes in case the URL has trailing slashes or parameters
    id_part = parts[-1].split('/')[0]
    
    return id_part

def getCompanyIdByCompanyLinkedInUrl(companyLinkedinUrl):

    companyDao = CompanyDao()
    companyUuid = companyDao.getCompanyUuidByLinkedInUrl(companyLinkedinUrl)

    return companyUuid

def doesLinkedInCompanyExist(individualJobRecord):

    companyDao = CompanyDao()
    doesCompanyExist = companyDao.doesCompanyExist(individualJobRecord["companyUrl"])

    return doesCompanyExist

def doesLinkedInJobExist(individualJobRecord):

    jobPostingDao = JobPostingDao()
    doesJobExist = jobPostingDao.checkIfJobExists(individualJobRecord['jobUrl'])

    return doesJobExist

"""
Call the JobPostingDao and have it update this job record for today's date
"""
def updateLinkedInJobRecord(individualJobRecord):

    jobPostingDao = JobPostingDao()
    jobPostingDao.updateLinkedInJobRecordUpdatedDate(individualJobRecord['jobUrl'])

    return

"""
This company needs to be inserted into the DB. We will prepare modify this dataframe to belike the company dataframe and then call the DAO

"""
def insertNewCompanyIntoDb(individualJobRecord):

    # Create an empty DataFrame with the specified columns
    companyDataFrame = pd.DataFrame(columns=[
        "company_id", "company_name", "company_website", "linkedin_url", "industry", 
        "num_employees", "ownership_type", "about_webpage", "careers_page", 
        "home_page_summary", "about_page_summary", "linkedin_company_summary", 
        "has_datascience", "has_product_operations"
    ])

    # Assign values to the specified columns
    # Create a new row with the specified values
    new_row = {
        "company_id": uuid.uuid4(),  # Generate a new UUID
        "company_name": individualJobRecord["companyName"],
        "company_website": None,
        "linkedin_url": individualJobRecord["companyUrl"],
        "industry": None,
        "num_employees": None,
        "ownership_type": None,
        "about_webpage": None,
        "careers_page": None,
        "home_page_summary": None,
        "about_page_summary": None,
        "linkedin_company_summary": None,
        "has_datascience": None,
        "has_product_operations": None
        }

    companyDataFrame = pd.concat([companyDataFrame, pd.DataFrame([new_row])], ignore_index=True)

    companyDao = CompanyDao()
    companyDao.insertCompany(companyDataFrame)

    return 

"""
Convert the individualJobRecord that represents data from the Apify Crawler to a Dataframe that represents a row in the Job Postings Table
Call the JobPostingDao and instert the record. 
"""
def insertNewLinkedInJobRecord(individualJobRecord):

    # Create an empty DataFrame with the specified columns
    jobpostingDataFrame = pd.DataFrame(columns=[
            "job_posting_id", "company_id", "posting_url", "posting_source", "posting_source_id", "job_title", 
            "full_posting_description", "job_description", "is_ai", "job_salary", "job_posting_company_information",
            "job_posting_date", "job_insertion_date", "job_last_collected_date", "job_active", "city", "state" 
    ])

    geographyHelper = GeographyHelper()
    cityStateDF = geographyHelper.getCityState(individualJobRecord["location"])


    # Assign values to the specified columns
    # Create a new row with the specified values
    new_row = {
        "job_posting_id": uuid.uuid4(),  # Generate a new UUID
        "company_id" : getCompanyIdByCompanyLinkedInUrl(individualJobRecord["companyUrl"]),
        "posting_url" : individualJobRecord["jobUrl"],
        "posting_source" : "linkedin",
        "posting_source_id" : getLinkedInJobRecordId(individualJobRecord["jobUrl"]),
        "job_title" : individualJobRecord["title"],
        "full_posting_description" : individualJobRecord["description"],
        "job_description" : None,
        "is_ai" : None,  
        "job_salary" : individualJobRecord["salary"],
        "job_posting_company_information" : None,
        "job_posting_date" : individualJobRecord["publishedAt"],
        "job_insertion_date" : datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S'), 
        "job_last_collected_date" : datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S'),
        "job_active" : True,
        "city": cityStateDF['city'].iloc[0],
        "state": cityStateDF['state'].iloc[0]

    }


    jobpostingDataFrame = pd.concat([jobpostingDataFrame, pd.DataFrame([new_row])], ignore_index=True)
    jobPostingDao = JobPostingDao()

    try:
        successStatus = jobPostingDao.insertNewJobRecord(jobpostingDataFrame)
        if successStatus == -1:
            raise Exception("Database insertion failed with status -1")
    except Exception as e:
        logging.error(f"Error inserting job record: {e}")
        # Save the job record to CSV for troubleshooting
        fileName = getLinkedInJobRecordId(individualJobRecord["jobUrl"]) + ".csv"
        jobpostingDataFrame.to_csv(fileName, index=False, encoding='utf-8')
        logging.info(f"Failed job record saved as CSV. Filename: {fileName}")
        return False

    return True

"""
-Check to see if this company exists, 
-If yes, then go ahead and instert this job. 
-If no, then first insert this company and then insert this job. 

"""
def processNewLinkedInJobRecord(individualJobRecord):

    # Call doesJobExist() with the current row. The below function will do the work to remove potential query strings
    doesCompanyExist = doesLinkedInCompanyExist(individualJobRecord)

    #If the Company is found in the DB, we will just need to create a new LinkedIn Job Record. 
    if doesCompanyExist:
        insertNewLinkedInJobRecord(individualJobRecord)
    
    #If the Company does not exist, we have to insert the company first. 
    #We will then insert the job record following the company
    else:
        insertNewCompanyIntoDb(individualJobRecord)
        insertNewLinkedInJobRecord(individualJobRecord)

    return

def ensureJobPostingHasDate(individualJobRecord):
    """
    If there is a date, just return the individualJobRecord
    If individualJobRecord["publishedAt"] does not have a date, apply today's date. 
    
    """
    if "publishedAt" not in individualJobRecord or not individualJobRecord["publishedAt"]:
        # Apply today's date in the specified format
        individualJobRecord["publishedAt"] = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')

    return individualJobRecord

def checkCompanyNameToSeeIfJunk(individualJobRecord):
    """
    We don't want to consider jobs for these companies:
        a
        a
        a
    
    We will call the JobDao and get the Company Name
    """
    companyLinkedinUrl = individualJobRecord['companyUrl']
    companyDao = CompanyDao()
    company_id = companyDao.getCompanyUuidByLinkedInUrl(companyLinkedinUrl)
    company_name = companyDao.getCompanyNameByCompanyId(company_id)

    #Relavtive File Path of JSON File with excluded companies
    json_relative_path = f"Configuration/ExcludedCompanies.json"
    script_dir = os.path.dirname(__file__)  
    abs_file_path = os.path.join(script_dir, json_relative_path)

    # Step 1: Open the JSON file
    with open(abs_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    excluded_companies = data.get("Companies", [])

    # Check if company_name is contained in the list of excluded companies. 
    # Return True if yes, False otherwise.
    return company_name in excluded_companies


def processJobRecord(individualJobRecord):
    """
    -First get the status to see if this job exists. 
    -If yes, then update the existing LinkedIn Record with new timestamp. 
    -If no, then insert the record into the DB. 

    """
    logging.info("Begin Processing an Individual Job Record")
    # Clean up the Job record by (1)  removing the potential query strings in the url (2) making sure there's a date for jobPosting. 
    individualJobRecord['jobUrl'] = remove_query_parameters(individualJobRecord['jobUrl'])
    individualJobRecord['companyUrl'] = remove_query_parameters(individualJobRecord['companyUrl'])
    individualJobRecord = ensureJobPostingHasDate(individualJobRecord)

    # Some companies aren't worth it. We will skip the whole insertion process if its a junk company
    """
    isJunkCompany = checkCompanyNameToSeeIfJunk(individualJobRecord)
    if isJunkCompany:
        return
    """
    # Call doesJobExist() with the current row. 
    doesJobExist = doesLinkedInJobExist(individualJobRecord)

    #If the Job is found in the DB, we will update the last observed date. 
    if doesJobExist:
        updateLinkedInJobRecord(individualJobRecord)
    
    #If the Job has not been seen before, we will create a new Job Record
    else:
        processNewLinkedInJobRecord(individualJobRecord)

    return

def persistFailedList():
    
    # Generate a random string of 5 alpha characters
    randomString = ''.join(random.choices(string.ascii_letters, k=5))

    # Construct the filename with the current date
    filename = f"JobPostingReports/failed_jobs_titles_{randomString}.txt"

    # Ensure the JobPostingReports directory exists
    
    if not os.path.exists('JobPostingReports'):
        os.makedirs('JobPostingReports')

    # Open the file for writing in the specified directory
    with open(filename, 'w') as file:
        # Write each job title to a line in the file
        for title in failedJobTitles:
            file.write(title + '\n')

    return

def cleanJobRecordData(apifyJobsReport):
    """
    This method is responsible for removing the query string in the urls that exist in the raw data and ensuring we have a posting date. 
    The method takes in a dataframe called apifyJobsReport. Two columns of interest in the DF: 
        1: companyUrl
        2: jobUrl


    The companyUrl and the jobUrl both have query strings that we can safely remove.
    We will iterate through each row in the dataframe and then clean these values. 
    We will return the cleaned dataframe. 

    """

    for _, row in apifyJobsReport.iterrows():
        
        row['jobUrl'] = remove_query_parameters(row['jobUrl'])
        row['companyUrl'] = remove_query_parameters(row['companyUrl'])
        row = ensureJobPostingHasDate(row)

    return apifyJobsReport

def getJobsThatAlreadyExist(df):
    """
    This method is reponsible for determining which jobs in the DF already exist in our DB. To do this we wil:
        Instantiate the Job Posting Dao and find the list of Jobs that already exist. 
        Return a DF that represents the union of the jobs in the Aprify Jobs report and the Job Postings Table

    
    """

    #JobPostingDao.getCurrentJobsIdsAsDataFrame() will return a DF that contains a column called posting_url
    jobPostingDao = JobPostingDao()
    currentJobs = JobPostingDao.getCurrentJobsIdsAsDataFrame()

    #We need to remove all jobs from the original DF for this method that are NOT found in the currentJobs.
    #We are returning a dataframe that shows the jobs that exist in BOTH

     # Compare and filter jobs: retain only the jobs that exist in both the input DF and the currentJobs DF
    commonJobs = pd.merge(df, currentJobs, how='inner', on='posting_url')

    # Return the DataFrame containing jobs that exist in both
    return commonJobs


def main(args):

    # Define the directories
    raw_collections_dir = "C:\\Users\\caraw\\OneDrive\\Documents\\PythonProjects\\OperationBattleshipParent\\OperationBattleshipDataPipeline\\RawCollections"
    processed_collections_dir = "C:\\Users\\caraw\\OneDrive\\Documents\\PythonProjects\\OperationBattleshipParent\\OperationBattleshipDataPipeline\\ProcessedCollections"

    # Get the list of JSON files in the raw collections folder
    files = [file for file in os.listdir(raw_collections_dir) if file.endswith('.json')]

    # Process each JSON file
    for file in files:
        file_path = os.path.join(raw_collections_dir, file)
        

        # Open and load the contents of the JSON file into a DataFrame
        with open(file_path, 'r', encoding='utf-8') as f:
             
            data = json.load(f)
            apifyJobsReport = pd.DataFrame(data)
            
        jobProcessedCount = 0
        # Process each job record in the DataFrame
        for _, row in apifyJobsReport.iterrows():

                start_time = time.time()
                processJobRecord(row)

                end_time = time.time()  # Capture end time
                duration_ms = (end_time - start_time) * 1000  # Calculate duration in milliseconds
                jobProcessedCount = jobProcessedCount + 1
                logging.info(f"Finished Processing a single Job Report File from Apify. This process took {duration_ms:.2f} milliseconds")
                logging.info(f"We have processed {jobProcessedCount} total jobs.")
                logging.info(f"Total Jobs that failed:  {failedJobsCount}.")
    
        #Save the list of job titles that failed to process. We can fix them later. 
        persistFailedList()

        # Save the processed DataFrame to a new file in the processed collections folder
        processed_file_path = os.path.join(processed_collections_dir, f"processed_{file}")
        apifyJobsReport.to_csv(processed_file_path, index=False)

        # Move the original JSON file to the processed collections folder
        shutil.move(file_path, processed_collections_dir)

    return


def newMain(args):

    """
    I want to explore a more efficient way to process the data. 
    I'll get a list of all Job IDs in the database and store in a list of some form. 

    I will them open a JSON File from the Raw Collections Folder,
    Create a list of jobs that are new and also a list of jobs that have been seen before. 
    This will save a lot of calls since we will already know which jobs just need an update time. We save at least one SQL Query for each job

    For the list of jobs that need inserted, we will do those first. 

    For the list of jobs that need updated, we will do a mass update for those jobs. 
    """



    # Define the directories
    raw_collections_dir = "C:\\Users\\caraw\\OneDrive\\Documents\\PythonProjects\\OperationBattleship\\RawCollections"
    processed_collections_dir = "C:\\Users\\caraw\\OneDrive\\Documents\\PythonProjects\\OperationBattleshipParent\\OperationBattleshipDataPipeline\\ProcessedCollections"

    # Get the list of JSON files in the raw collections folder
    files = [file for file in os.listdir(raw_collections_dir) if file.endswith('.json')]

    # Process each JSON file
    for file in files:
        file_path = os.path.join(raw_collections_dir, file)
        

        # Open and load the contents of the JSON file into a DataFrame
        with open(file_path, 'r', encoding='utf-8') as f:
             
            data = json.load(f)
            apifyJobsReport = pd.DataFrame(data)

        apifyJobsReport= cleanJobRecordData(apifyJobsReport)

        existingJobsAsDataFrame = getJobsThatAlreadyExist(apifyJobsReport)
        # Find new jobs to process
        # Perform a left join and then filter the entries that are only in the apifyJobsReport
        newJobsToProcessAsDataFrame = apifyJobsReport.merge(existingJobsAsDataFrame, 
                                                            how='left', 
                                                            on='posting_url', 
                                                            indicator=True).loc[lambda x : x['_merge']=='left_only']

        # Drop the merge indicator column as it's no longer needed
        newJobsToProcessAsDataFrame = newJobsToProcessAsDataFrame.drop(columns=['_merge'])

            
        jobProcessedCount = 0
        # Process each job record in the DataFrame
        for _, row in newJobsToProcessAsDataFrame.iterrows():
                start_time = time.time()
                
                # Do things here

                end_time = time.time()  # Capture end time
                duration_ms = (end_time - start_time) * 1000  # Calculate duration in milliseconds
                jobProcessedCount = jobProcessedCount + 1
                logging.info(f"Finished Processing a single Job Report File from Apify. This process took {duration_ms:.2f} milliseconds")
                logging.info(f"We have processed {jobProcessedCount} total jobs.")
                logging.info(f"Total Jobs that failed:  {failedJobsCount}.")
    
        #Save the list of job titles that failed to process. We can fix them later. 
        persistFailedList()

        # Save the processed DataFrame to a new file in the processed collections folder
        processed_file_path = os.path.join(processed_collections_dir, f"processed_{file}")
        apifyJobsReport.to_csv(processed_file_path, index=False)

        # Move the original JSON file to the processed collections folder
        shutil.move(file_path, processed_collections_dir)

    return


if __name__ == "__main__":
    import sys
    # Convert command line arguments to a dictionary or any suitable format
    args = {"name": sys.argv[1]} if len(sys.argv) > 1 else {}
    main(args)