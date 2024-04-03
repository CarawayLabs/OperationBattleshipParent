"""

This Python script, which is the sole interface with the Apify SDK in this project, is designed to fetch job data from the Apify Job Crawler. It contains the ApifyJobsCaller class with methods to execute new job crawlers, retrieve product manager jobs, and fetch all jobs for a given set of companies.

The execute_new_jobs_crawler method is the primary function that interacts with the Apify SDK. It accepts a job title and duration as parameters, prepares the actor input based on the duration, runs the actor, fetches the data, and stores it in a list. The data is then saved to a JSON file in the RawCollections directory.

The get_product_manager_jobs and get_all_jobs_for_companies methods are placeholders for fetching specific job data. The former is intended to retrieve all product manager jobs, while the latter is designed to return all jobs for a given list of companies.

This script uses environment variables for sensitive data like the Apify token, which should be stored in a .env file in the same directory.
"""

import os
import json
import logging
import random
import string
from datetime import datetime
from dotenv import load_dotenv
from apify_client import ApifyClient



# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv('.env')

class ApifyJobsCaller:
    def __init__(self):
        logging.info(f"{self.__class__.__name__} class initialized")



    
    #This function will call the Apify Python SDK and run the job. It requires a job title. 
    #The expectation is that this is the only function that actually calls the API SDK. 
    def execute_new_jobs_crawler(self, job_title_name, duration):
        logging.info(f"Beginning the process for collecting {job_title_name} jobs from Apify Job Crawler")

        apifytokenFromEnv = os.getenv("APIFY_CLIENT_TOKEN")  # Ensure correct environment variable name
        client = ApifyClient(apifytokenFromEnv)

        # Prepare the Actor input based on duration
        publishedAt = ""  # Default to empty, assuming it handles 'anytime' if not provided
        if duration == 1:
            publishedAt = "r86400"  # last 24 hours
        elif duration == 7: 
            publishedAt = "r604800"  # last week
        elif duration == 30:
            publishedAt = "r2592000"  # last month
        elif duration == 100:
            publishedAt = None  # Set to None for clarity, indicating no value

        logging.info(f"Based on the args, we have set publishedAt value for Apify Caller to: {publishedAt}")

        # Prepare the run_input, conditionally adding 'publishedAt' only if it's not None
        run_input = {
            "location": "United States",
            "rows": 1000,
            "title": job_title_name,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
                }
        }

        if publishedAt is not None:
            run_input["publishedAt"] = publishedAt
        # Run the Actor and wait for it to finish
        run = client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)

        # Fetch the data and store it in a list
        data_list = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            data_list.append(item)

        # Ensure RawCollections folder exists
        raw_collections_folder = os.path.join("C:/Users/caraw/OneDrive/Documents/PythonProjects/OperationBattleshipParent/OperationBattleshipDataPipeline/RawCollections")

        os.makedirs(raw_collections_folder, exist_ok=True)

        # Generate file name as a random 4 digit string. Save as json. 
        randomString = ''.join(random.choices(string.ascii_lowercase, k=4))
        file_name = f'{randomString}.json'  # Concatenate for the file name

        # Construct the full file path
        full_file_path = os.path.join(raw_collections_folder, file_name)

        # Write the list to the file in JSON format
        with open(full_file_path, 'w') as file:
            json.dump(data_list, file, indent=4)

        logging.info(f"Data saved to {full_file_path}")
        
        return full_file_path


    #This function gets all of the Product Manager Jobs. 
    def get_product_manager_jobs(self):

        return
            

    
    #When given a collection of company names, find all the jobs open for this company.
    #Returns a JSON of Jobs from Apify
    def get_all_jobs_for_companies(self, compmany_dataframe):

        print("You;ve enetered the get all jobs for company method")

        return 
    