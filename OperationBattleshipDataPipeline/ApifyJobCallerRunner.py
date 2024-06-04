"""
This Script is used to call the ApifyJobsCaller Class.
When given a list of different job titles, this script will iterate through those and call the ApifyJobsCaller.  

"""

import os
import inspect
import json
import sys
import logging
import time
import random
import string
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from operation_battleship_common_utilities.ApifyJobsCaller import ApifyJobsCaller

def createJobsReport(fileName, duration):
    script_name = os.path.basename(__file__)
    func_name = inspect.currentframe().f_code.co_name
    logging.debug(f"We have entered {func_name} function in script {script_name}")
    

    #Construct the file path for the JSON file with the Job Roles    
    json_relative_path = f"Configuration/{fileName}"
    script_dir = os.path.dirname(__file__)  
    abs_file_path = os.path.join(script_dir, json_relative_path)
    
    # Step 1: Open the JSON file
    with open(abs_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract the list of roles from the JSON
    roles = data.get("Roles", [])

    # Loop through the roles and call ApifyJobsCaller
    persistedFiles = []
    for role in roles:
        apifyJobsCrawler = ApifyJobsCaller()
        jobReportFileName = apifyJobsCrawler.execute_new_jobs_crawler(role["title"], duration)
        time.sleep(10)
        persistedFiles.append(jobReportFileName )

    return persistedFiles

def removeDuplicates(persistedFiles):
    """
    This function takes in a list of files that have been saved to disk. These files are JSON files that contain output of recent runs for the Apify Jobs Crawler

    The purpose of the function is to open each file and merge all the results into a master JSON file and remove any duplicates. 
    We define the uniqueness of a JSON object based on the jobUrl attribute. If two different JSON objects contain the same jobUrl, then we would only need one of these as they represent an identical job. 

    Once we have a master JSON object, we will then chunk into 300 records each. 
    Then persist each JSON to the RawCollections Folder
    We will then delete all files in the persistedFiles list

    The function will return when this is complete
    """

    script_name = os.path.basename(__file__)
    func_name = inspect.currentframe().f_code.co_name
    logging.debug(f"We have entered {func_name} function in script {script_name}")

    # Initialize an empty list to store all JSON objects
    all_jobs = []

    # Read and accumulate JSON objects from each file
    for file_path in persistedFiles:
        with open(file_path, 'r') as file:
            jobs = json.load(file)
            all_jobs.extend(jobs)

    # Remove duplicates based on jobUrl
    unique_jobs = []
    seen_urls = set()
    for job in all_jobs:
        if job['jobUrl'] not in seen_urls:
            seen_urls.add(job['jobUrl'])
            unique_jobs.append(job)

    # Chunk the unique jobs into sets of 300
    chunk_size = 300
    chunks = [unique_jobs[i:i + chunk_size] for i in range(0, len(unique_jobs), chunk_size)]

    # Ensure the RawCollections folder exists
    raw_collections_folder = os.path.join("C:/Users/caraw/OneDrive/Documents/PythonProjects/OperationBattleshipParent/OperationBattleshipDataPipeline/RawCollections")
    os.makedirs(raw_collections_folder, exist_ok=True)

    # Save each chunk to a separate file
    current_date = datetime.now().strftime("%b%d")
    for i, chunk in enumerate(chunks, start=1):
        random_suffix = ''.join(random.choices(string.ascii_lowercase, k=4))
        chunk_file_name = f"master_jobs_{current_date}_{i}_{random_suffix}.json"
        chunk_file_path = os.path.join(raw_collections_folder, chunk_file_name)
        with open(chunk_file_path, 'w') as chunk_file:
            json.dump(chunk, chunk_file, indent=4)

    # Delete the original files
    for file_path in persistedFiles:
        os.remove(file_path)

def main(fileName, duration):
    """
    Main function will call the createJobsReport Function to generate the list of all open jobs on LinkedIn for Job Titles provided in the productManagerJobTitles.json file.

    After that function returns, Main will call the removeDuplicates() function that combines on of the jobs into a single job report.  
    """

    persistedFiles = createJobsReport(fileName, duration)
    removeDuplicates(persistedFiles)

    return 


"""
This script is expecting two arguments
1: Filename for the Job Titles
2: Number of days for the "published at" setting. This can be a discrete value of 1 day, 7 days, 30 days, all.
    The possible values are 1, 7, 30, all

If the script has zero arguements, we will asssume:
1: AiPmJobTitles.json
2: 1 day
"""
if __name__ == "__main__":
    import sys
    # Default values
    #defaultFileName = "AiPmJobTitles.json"
    #defaultFileName = "DsJobTitles.json"
    defaultFileName = "UxResearchJobTitles.json"
    defaultDuration = 7

    # Extract arguments with default values
    fileName = sys.argv[1] if len(sys.argv) > 1 else defaultFileName
    # Attempt to convert the second argument to an integer if present, or use the default duration
    try:
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else defaultDuration
    except ValueError:
        # Handle the case where the second argument is not a valid integer
        logging.warn("Warning: Duration argument is invalid. Using default value of 1.")
        duration = defaultDuration

    logging.info(f"Script is using filename: {fileName} and time setting: {duration}")
    main(fileName, duration)

