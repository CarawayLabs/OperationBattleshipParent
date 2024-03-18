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

# Get the directory of the script being run:
current_script_path = os.path.abspath(__file__)

# Get the parent directory of the current script:
parent_directory = os.path.dirname(os.path.dirname(current_script_path))

# Add the parent directory to the sys.path:
if parent_directory not in sys.path:
    sys.path.append(parent_directory)

from CommonUtilities.OpenAICaller import OpenAICaller
from CommonUtilities.JobPostingDao import JobPostingDao
from CommonUtilities.CandidateRequirementsDao import CandidateRequirementsDao
from CommonUtilities.JobResponsibilitiesDao import JobResponsibilitiesDao
from CommonUtilities.JobSkillsDao import JobSkillsDao
from CommonUtilities.JobKeyWordsDao import JobKeyWordsDao
from CommonUtilities.FailureLogger import FailureLogger
from CommonUtilities.JobTitleCategoryClassifier import JobTitleCategoryClassifier


load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
    


def enrichJobRecordDetails(job_record):
    """
    Job record is a dataframe and contains several columns. One of which is full_posting_description
    The function will call ChatGPT and ask it to classify further information about this job record based on the given job description. 
    ChatGPT will return a JSON Object. 

    Based on different attributes of the JSON, we will create dataframes and insert records into DB. 

    """
    
    
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
        #We should add logic in here that asserts all the expected fields are in the JSON. Will keep calling the LLM until it has the expected fields. 
        languageModelResponse = json.loads(languageModelResponse)

        attribute_names = languageModelResponse.keys()
        logging.info(f"Attribute names in the JSON: {attribute_names}")
            
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

        #Add the new job category
        jobTitleCategoryClassifier = JobTitleCategoryClassifier()
        job_record["job_category"] = jobTitleCategoryClassifier.get_job_category(job_record["job_title"]) 


        jobPostingDao = JobPostingDao()
        jobPostingDao.update_job_posting(job_record)

        """
        The code above is probable pretty good.
        Missing Stepes are stubbed out below.  
        I have three tables that will need data. I add data to these using a Python DAO Class. 
        1: Candidate_Requirements
        2: Job_Responsibilities
        3: Job Skills
        4: Job_Keywords

        The data for these tables is found in the JSON from languageModelResponse.
        1: (Postgres Table Name) Candidate_Requirements - (languageModelResponse JSON)
        2: (Postgres Table Name) Job_Responsibilities (languageModelResponse JSON)
        3: (Postgres Table Name) Job_Keywords (languageModelResponse JSON)

        Can I associate the JSON Object / List with the new DF?
        Can I get the new DF to be saved into the DB via the JobPostingDao
        Now do it for the other two types also. 

        candidateRequirementsDao
        job_responsibilities
        JobKeyWordsDao


        """

        #1: Candidate_Requirements
        
        #The LLM does a better job to parse the data when we call it "job_requirements". But I chose a different name for the datamodel. 
        candidateRequirementsJSON = languageModelResponse.get("job_requirements", [])
        
        # Create a DataFrame to hold the Candidate Requirements
        candidateRequirementsDataframe = pd.DataFrame(candidateRequirementsJSON, columns=['item'])
        
        candidateRequirementsDataframe['job_posting_id'] = job_record["job_posting_id"]
        candidateRequirementsDataframe['unique_id'] = [uuid.uuid4() for _ in range(len(candidateRequirementsDataframe))]    
        # Reorder the columns as requested
        candidateRequirementsDataframe = candidateRequirementsDataframe[['job_posting_id', 'unique_id', 'item']]

        candidateRequirementsDao = CandidateRequirementsDao()
        candidateRequirementsDao.insertRequirementsForJobPosting(candidateRequirementsDataframe)

        #2: Job_Responsibilities
        job_responsibilitiesJSON = languageModelResponse.get("job_responsibilities", [])
        
        # Create a DataFrame to hold the job responsibilities
        job_responsibilitiesDataframe = pd.DataFrame(job_responsibilitiesJSON, columns=['item'])
        
        job_responsibilitiesDataframe['job_posting_id'] = job_record["job_posting_id"]
        job_responsibilitiesDataframe['unique_id'] = [uuid.uuid4() for _ in range(len(job_responsibilitiesDataframe))]    
        # Reorder the columns as requested
        job_responsibilitiesDataframe = job_responsibilitiesDataframe[['job_posting_id', 'unique_id', 'item']]

        jobResponsibilitiesDao = JobResponsibilitiesDao()
        jobResponsibilitiesDao.insertJobResponsibilitiesForJobPosting(job_responsibilitiesDataframe)
        
        #3: Job Skills
        job_skillsJSON = languageModelResponse.get("job_skills", [])
        
        # Create a DataFrame to hold the job skills
        job_skillsDataframe = pd.DataFrame(job_skillsJSON, columns=['item'])
        
        job_skillsDataframe['job_posting_id'] = job_record["job_posting_id"]
        job_skillsDataframe['unique_id'] = [uuid.uuid4() for _ in range(len(job_skillsDataframe))]    
        # Reorder the columns as requested
        job_skillsDataframe = job_skillsDataframe[['job_posting_id', 'unique_id', 'item']]

        jobSkillsDao = JobSkillsDao()
        jobSkillsDao.insertSkillsForJobPosting(job_skillsDataframe)  
        
        #4: Job_Keywords
        jobKeyWordsJSON = languageModelResponse.get("job_keywords", [])
        
        # Create a DataFrame to hold the job key words
        jobKeyWordsDataFrame = pd.DataFrame(jobKeyWordsJSON, columns=['item'])
        
        jobKeyWordsDataFrame['job_posting_id'] = job_record["job_posting_id"]
        jobKeyWordsDataFrame['unique_id'] = [uuid.uuid4() for _ in range(len(jobKeyWordsDataFrame))]    
        # Reorder the columns as requested
        jobKeyWordsDataFrame = jobKeyWordsDataFrame[['job_posting_id', 'unique_id', 'item']]

        jobKeyWordsDao = JobKeyWordsDao()
        jobKeyWordsDao.insertJobKeyWordsForJobPosting(jobKeyWordsDataFrame)

        return

    
    except Exception as e:
            print("Some error occurred the error string:", e)
            print("Saving info to disk for later inspection.")
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
        print("No unprocessed jobs to classify")
        return

    # Iterate through each job record in the DataFrame
    start_time = time.time() 
    for index, job_record in job_records.iterrows():
        job_start_time = time.time()
        try:
            # Attempt to call the classify function for each job record
            enrichJobRecordDetails(job_record)

            logging.info(f"Finished calling the LLM for a single job. Job Title = {job_record['job_title']} ")
            totalRecords += 1

        except Exception as e:
            # Log the exception and skip to the next job record
            logging.error(f"Error processing job record {job_record['job_title']}: {e}")

        finally:
            job_end_time = time.time()  # Capture end time
            duration_ms = (job_end_time - job_start_time) * 1000  # Calculate duration in milliseconds

            # These logging statements will execute whether or not an exception occurred
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

    # We will first get a record of all the jobs which have not been classified. 
    unprocessed_jobs = getUnprocessedAiClassificationJobs()

    # Once we've got the list of jobs to process, 
    # We send the dataframe to a function that will call the LLM and get more structured and robust data about the jobs. 
    # Finally, each job is then saved to the database. 
    enrichEachJobAndPersistToDatabase(unprocessed_jobs)

    return 


if __name__ == "__main__":
    import sys
    # Convert command line arguments to a dictionary or any suitable format
    args = {"name": sys.argv[1]} if len(sys.argv) > 1 else {}
    main(args)