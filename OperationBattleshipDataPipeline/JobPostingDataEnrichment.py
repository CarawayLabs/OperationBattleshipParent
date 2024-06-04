"""
This script is responsible for imprvoing the level of detail that we have about a job. 
-Is is an AI Job?
-Is it a GenAI Job?
-Salary Details
-Location Information


General Flow of Script:
-Get a list of all records in the table where isAI field is null
-for each record, we want to pull the job description and then call chat GPT to ask for it to parse the job description and determine if this is an AI job or not. 
-output of chatgpt will be a json file so that I can parse it. 
{
isAI : true
reasoning : "Why was it predicted to be AI or not"

}



"""

import os
import inspect
import json
import sys
import time
import logging
import uuid 
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

import boto3
from botocore.client import Config

from operation_battleship_common_utilities.JobPostingDao import JobPostingDao
from operation_battleship_common_utilities.CandidateRequirementsDao import CandidateRequirementsDao
from operation_battleship_common_utilities.JobResponsibilitiesDao import JobResponsibilitiesDao
from operation_battleship_common_utilities.JobSkillsDao import JobSkillsDao
from operation_battleship_common_utilities.JobKeyWordsDao import JobKeyWordsDao
from operation_battleship_common_utilities.JobTitleCategoryClassifier import JobTitleCategoryClassifier
from operation_battleship_common_utilities.FailureLogger import FailureLogger

from operation_battleship_common_utilities.NomicAICaller import NomicAICaller
from operation_battleship_common_utilities.OpenAICaller import OpenAICaller
from operation_battleship_common_utilities.PineConeDatabaseCaller import PineConeDatabaseCaller


load_dotenv()

log_file_path = os.path.join(Path(__file__).parent.absolute(), 'logfile.log')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s',
                    filename=log_file_path,
                    filemode='w')
def saveLlmQuestionResponsePair(job_posting_id, llmChain, languageModelResponse):
    """
    This function is used to save the LLM input and output to an S3 Bucket on Digital Ocean. 
    We will be using a folder called, "llm".
    We will create a new folder in this directory that is the job_posting_id
    We will then write the llmChain in a file. It will be called llmChain.txt
    We will then wrtie the languageModelResponse in a file. It will be called languageModelResponse.txt

    Args
        job_posting_id - This is a UUID that represents the identifier for this job posting.
        llmChain - This is a <class 'list'>. It is the prompting that we insert to the LLM
        languageModelResponse - <class 'dict'>. It is intended to be a JSON object that is output from the LLM to give structure to the job posting.    

    Return Value
        none
    """
    print(type(llmChain))

    print(type(languageModelResponse))

    # Convert each item in llmChain to a string
    llmChain_str = '\n'.join(json.dumps(item) if isinstance(item, dict) else str(item) for item in llmChain)
    languageModelResponse_str = json.dumps(languageModelResponse, indent=4)

    # DigitalOcean Spaces settings
    region_name = 'nyc3'
    endpoint_url = 'https://nyc3.digitaloceanspaces.com'
    bucket_name = 'operationbattleship-resumes'
    folder_name = 'llm'

    # Initialize a session using DigitalOcean Spaces
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name=region_name,
                            endpoint_url=endpoint_url,
                            aws_access_key_id=os.getenv('DO_SPACES_KEY'),
                            aws_secret_access_key=os.getenv('DO_SPACES_SECRET'))

    # Define the object keys (file paths) within the Space
    llmChain_key = f'{folder_name}/{job_posting_id}/llmChain.txt'
    languageModelResponse_key = f'{folder_name}/{job_posting_id}/languageModelResponse.txt'

    try:
        # Upload llmChain to DigitalOcean Space
        client.put_object(Bucket=bucket_name, Key=llmChain_key, Body=llmChain_str, ACL='public-read-write')

        # Upload languageModelResponse to DigitalOcean Space
        client.put_object(Bucket=bucket_name, Key=languageModelResponse_key, Body=languageModelResponse_str, ACL='public-read-write')

        print("Files uploaded successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return
#Function to generate a prompt for the LLM that has the purpose of classifiying the job details
def createPromptFromJobDescription(description, salary_range):

    promptMessagesAsJsonFileRelativePath = 'LlmTemplates/JobPostingClassifierPromptChainJsonSchema.json'
    
    # Get the absolute path of the script
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    abs_file_path = os.path.join(script_dir, promptMessagesAsJsonFileRelativePath)
    
    # Step 1: Open the JSON file
    with open(abs_file_path, 'r', encoding='utf-8') as file:
        promptMessagesAsDataframe = json.load(file)

    description_str = description if description is not None else "No description provided"
    salary_range_str = salary_range if salary_range is not None else "No salary range provided"
    userInput = description_str + "\n Listed Salary Range: " + salary_range_str + " Reminder: You need to respond with well formed JSON."

    messages=[
        {
        "role": "system",
        "content": promptMessagesAsDataframe["systemContentOne"]
        },        
        {
        "role": "user",
        "content": promptMessagesAsDataframe["userContentOne"]
        },
        {
        "role": "assistant",
        "content": promptMessagesAsDataframe["assistantContentOne"]
        },
        {
        "role": "user",
        "content": promptMessagesAsDataframe["userContentTwo"]
        },
        {
        "role": "assistant",
        "content": promptMessagesAsDataframe["AssistantContentTwo"]
        },
        {
        "role": "user",
        "content": userInput
        }
    ]

    return messages

# Function to get unprocessed AI classification jobs
def getUnprocessedAiClassificationJobs():

    jobPostingDao = JobPostingDao()
    #jobsToCategorize = jobPostingDao.fetchJobsRequiringEnrichment()
    jobsToCategorize = jobPostingDao.fetchPmJobsRequiringEnrichment()
    return jobsToCategorize


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

def embedTextAndAddMetadata(job_record, columnToEmbed):
    
    data = {}
    nomicAICaller = NomicAICaller()
    job_record = cleanAllValues(job_record)

    textToEmbed = job_record[columnToEmbed]
    embedding = nomicAICaller.embedDocument(textToEmbed)
    
    job_posting_id = job_record["job_posting_id"]

    metadata = {
        'is_ai': job_record['is_ai'],
        'is_genai': job_record['is_genai'],
        'salary_low': job_record['salary_low'], 
        'salary_midpoint': job_record['salary_midpoint'],
        'salary_high': job_record['salary_high'], 
        'job_category': job_record['job_category'],
        'job_posting_date': convertDateToInt(str(job_record['job_posting_date'])), 
        'work_location_type': job_record['work_location_type'],
    }
    data[job_posting_id] = {'embedding': embedding, 'metadata': metadata}
    
    return data

def convertDateToInt(date_str, epoch_str='1970-01-01'):

    date = datetime.strptime(date_str, '%Y-%m-%d')
    epoch = datetime.strptime(epoch_str, '%Y-%m-%d')
    delta = date - epoch
    return delta.days


def upsertIntoPinecone(indexName, nameSpace, embeddedJobPosting):

    pineConeKey = os.getenv("PINECONE_API_KEY")
    pineConeDatabaseCaller = PineConeDatabaseCaller(pineConeKey)
    pineConeDatabaseCaller.upsertEmbeddings(indexName, nameSpace, embeddedJobPosting)

    return

def embedAndUpsertRelevantDocumentsToPinecone(job_record):

    index = "job-postings"

    embeddedJobPosting = embedTextAndAddMetadata(job_record, "full_posting_description")
    upsertIntoPinecone(index, "full-posting-description", embeddedJobPosting)

    embeddedJobPosting = embedTextAndAddMetadata(job_record, "job_title")
    upsertIntoPinecone(index, "job-title", embeddedJobPosting)

    embeddedJobPosting = embedTextAndAddMetadata(job_record, "job_description")
    upsertIntoPinecone(index, "short-job-description", embeddedJobPosting)

    return 

def dropUnneededColumns(job_record):
    """
    This object type for this function is: <class 'pandas.core.series.Series'>

    We want to drop the columns below and then return the object
    """
    columns_to_drop = [ 
        'kmeansclusterid', 
        'dbscanclusterid', 
        'opticsclusterid', 
        'kmeansclustertopicname', 
        'dbscanclustertopicname', 
        'opticsclustertopicname'
    ]
    
    # Assuming job_record is part of a DataFrame, we can access the DataFrame using job_record.name
    df = job_record.to_frame().T
    df = df.drop(columns=columns_to_drop, errors='ignore')
    
    # Convert back to Series and return
    job_record_cleaned = df.iloc[0]
    return job_record_cleaned

def genericJobPostingAttributeInserter(job_record, json_key, dataframe_columns, dao_instance, languageModelResponse):
    """
    Inserts job posting attributes into the database using the specified DAO instance.
    
    Parameters:
    - job_record: The job record containing job posting details.
    - json_key: Key to access the relevant list in the languageModelResponse JSON.
    - dataframe_columns: Columns to use when creating the DataFrame from the JSON list.
    - dao_instance: An instance of the DAO class to use for inserting the DataFrame into the database.
    """
    # Extract the JSON list using the provided key
    json_list = languageModelResponse.get(json_key, [])
    
    # Create a DataFrame to hold the attributes
    attributes_dataframe = pd.DataFrame(json_list, columns=[dataframe_columns])
    
    # Add job_posting_id and generate unique IDs
    attributes_dataframe['job_posting_id'] = job_record["job_posting_id"]
    attributes_dataframe['unique_id'] = [uuid.uuid4() for _ in range(len(attributes_dataframe))]
    
    # Reorder the columns if necessary
    attributes_dataframe = attributes_dataframe[['job_posting_id', 'unique_id', dataframe_columns]]
    
    # Use the provided DAO instance to insert the DataFrame into the database
    dao_instance.insertMethod(attributes_dataframe)  # Note: Adjust `insertMethod` to match the actual method name in your DAO classes.

    return

def process_and_insert(data_json, dao_class, dao_method, job_record):
    dataframe = pd.DataFrame(data_json, columns=['item'])
    dataframe['job_posting_id'] = job_record["job_posting_id"]
    dataframe['unique_id'] = [uuid.uuid4() for _ in range(len(dataframe))]
    dataframe = dataframe[['job_posting_id', 'unique_id', 'item']]
    dao_instance = dao_class()
    getattr(dao_instance, dao_method)(dataframe)

def enrichJobRecordDetails(job_record):
    """
    Job record is a dataframe and contains several columns. One of which is full_posting_description
    The function will call ChatGPT and ask it to classify further information about this job record based on the given job description. 
    ChatGPT will return a JSON Object. 

    Based on different attributes of the JSON, we will create dataframes and insert records into DB. 
    """

    logging.info(f"Type of the job_record: {type(job_record)}")
        
    # Crafting a prompt for the language model
    description = job_record["full_posting_description"]
    salary_range = job_record["job_salary"]
    llmChain = createPromptFromJobDescription(description, salary_range)
    
    # Call the OpenAI API with the job description
    open_ai_caller = OpenAICaller()
    languageModelResponse = open_ai_caller.get_completion(llmChain)

    # Exit the function if the response is empty or None
    if not languageModelResponse or not languageModelResponse.strip():
        return  

    try: 
        # We should add logic in here that asserts all the expected fields are in the JSON. Will keep calling the LLM until it has the expected fields. 
        languageModelResponse = json.loads(languageModelResponse)

        saveLlmQuestionResponsePair(job_record["job_posting_id"], llmChain, languageModelResponse)

        logging.debug(f"Attribute names in the JSON: {languageModelResponse.keys()}")
            
        job_record["job_description"] = languageModelResponse["job_description"]
        job_record["is_ai"] = languageModelResponse["is_ai"]
        job_record["job_salary"] = languageModelResponse["job_salary"]
        job_record["job_posting_company_information"] = languageModelResponse["job_posting_company_information"]
        job_record["is_genai"] = languageModelResponse["is_genAi"]
        job_record["is_ai_justification"] = languageModelResponse["is_Ai_justification"]
        job_record["salary_low"] = languageModelResponse["salary_low"]
        job_record["salary_midpoint"] = languageModelResponse["salary_midpoint"]
        job_record["salary_high"] = languageModelResponse["salary_high"]
        job_record["city"] = languageModelResponse["city"]
        job_record["state"] = languageModelResponse["state"]
        job_record["work_location_type"] = languageModelResponse["work_location_type"]

        # Add the new job category
        jobTitleCategoryClassifier = JobTitleCategoryClassifier()
        job_record["job_category"] = jobTitleCategoryClassifier.get_job_category(job_record["job_title"])

        # Drop some of our columns so we can insert into PostGres and Pinecone        
        job_record = dropUnneededColumns(job_record) 
        
        jobPostingDao = JobPostingDao()
        jobPostingDao.update_job_posting(job_record)

        # Process and insert data into corresponding DAOs
        process_and_insert(languageModelResponse.get("job_requirements", []), CandidateRequirementsDao, 'insertRequirementsForJobPosting', job_record)
        process_and_insert(languageModelResponse.get("job_responsibilities", []), JobResponsibilitiesDao, 'insertJobResponsibilitiesForJobPosting', job_record)
        process_and_insert(languageModelResponse.get("job_skills", []), JobSkillsDao, 'insertSkillsForJobPosting', job_record)
        process_and_insert(languageModelResponse.get("job_keywords", []), JobKeyWordsDao, 'insertJobKeyWordsForJobPosting', job_record)

        embedAndUpsertRelevantDocumentsToPinecone(job_record)
    
    except Exception as e:
            logging.error(f"Some error occurred during processing. The error string is: {e}")
            logging.error(f"Saving info to disk for later inspection.")
            failureLogger = FailureLogger()
            failureLogger.logFailedLlmJsonResponse(job_record, languageModelResponse)
            return
    
#This function will take in a collection of job records as rows in a Pandas DataFrame. 
#It will iterate on each record and send to another method to apply classification to the individual record. 
#Once all records have been classified, the method will return the collection of job records. 
def enrichEachJobAndPersistToDatabase(job_records):
    totalRecords=0

    # Ensure unprocessed_jobs is a DataFrame and not None
    if job_records is None or job_records.empty:
        logging.info(f"No unnprocessed jobs to enrich. Exiting script.")
        return


    start_time = time.time() 
    for index, job_record in job_records.iterrows():
        job_start_time = time.time()
        try:
            enrichJobRecordDetails(job_record)

            logging.info(f"Finished calling the LLM for a single job. Job Title = {job_record['job_title']} ")
            totalRecords += 1

        except Exception as e:
            logging.error(f"Error processing job record {job_record['job_title']}: {e}")

        finally:
            job_end_time = time.time()  # Capture end time
            duration_ms = (job_end_time - job_start_time) * 1000  # Calculate duration in milliseconds

            logging.info(f"We have categorized {totalRecords} total jobs")
            logging.info(f"There are {job_records.shape[0]} total jobs to be processed")
            logging.info(f"Last record to update took {duration_ms:.2f} milliseconds")
    
    last_record_end_time = time.time()
    allUpdatesDuration = (last_record_end_time - start_time) * 1000
    logging.info(f"Finished calling the LLM for all jobs in the dataframe. This process took {allUpdatesDuration:.2f} milliseconds")
    return 

def main(args):

    func_name = inspect.currentframe().f_code.co_name
    logging.info(f"We have entered {func_name}")

    unprocessed_jobs = getUnprocessedAiClassificationJobs()
    # Create a new dataframe for UX related jobs
    #ux_jobs = unprocessed_jobs[unprocessed_jobs['job_title'].str.contains('user|researcher|ux', case=False, na=False)]
    
    unprocessed_jobs = unprocessed_jobs.sort_values(by='job_posting_date', ascending=False).head(500)  
    enrichEachJobAndPersistToDatabase(unprocessed_jobs)

    return 

if __name__ == "__main__":
    
    args = {"name": sys.argv[1]} if len(sys.argv) > 1 else {}
    main(args)