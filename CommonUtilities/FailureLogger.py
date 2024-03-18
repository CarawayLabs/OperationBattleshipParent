"""
This Python script defines a FailureLogger class that logs failed responses from a Language Learning Model (LLM) and the associated job record to disk for later analysis. The script is designed to handle situations where the LLM fails to create a well-formed JSON response. In such cases, the LLM response and the job title are saved to disk in a new folder within the ‘llmFailures’ directory. Each new folder is named with a random 5-digit string for uniqueness. The LLM response is saved as a JSON file, and the job record is saved as a CSV file. The script uses environment variables for secure operations and includes logging for tracking operations and errors. The FailureLogger class is initialized with no arguments, and the logFailedLlmJsonResponse method takes two arguments: the job record and the LLM response.
"""

import os
import json
import logging
import random
from dotenv import load_dotenv
import csv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv('.env')

class FailureLogger:
    def __init__(self):
        logging.info(f"{self.__class__.__name__} class initialized")
        self.base_failure_dir = 'llmFailures'
        # Ensure the base directory exists
        if not os.path.exists(self.base_failure_dir):
            os.makedirs(self.base_failure_dir)
            logging.info(f"Created base directory for failures: {self.base_failure_dir}")

    def logFailedLlmJsonResponse(self, job_record, languageModelResponse):
        """
        We will create a new folder in the llmFailures Folder. The new folder will be a random 5 digit string.
        In the folder we will save the languageModelResponse as a JSON file. Filename is llmResponse.json
        In the folder we will save the job_record to CSV. The name is created from the job_record[job_title]
        """
        logging.info("Logging information about the failed job posting enrichment to disk.")

        # Generate a random 5-digit string
        folder_name = ''.join(random.choices('0123456789', k=5))
        folder_path = os.path.join(self.base_failure_dir, folder_name)
        
        # Create the new folder
        os.makedirs(folder_path, exist_ok=True)

        # Save the languageModelResponse as a JSON file
        llm_response_path = os.path.join(folder_path, 'llmResponse.json')
        with open(llm_response_path, 'w') as f:
            json.dump(languageModelResponse, f, indent=4)
        logging.info(f"Saved language model response to {llm_response_path}")

        # Convert job_record to CSV and save
        job_title_safe = ''.join(e for e in job_record['job_title'] if e.isalnum() or e in [' ', '_', '-']).rstrip()
        job_record_path = os.path.join(folder_path, f"{job_title_safe}.csv")
        with open(job_record_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(job_record.keys())
            writer.writerow(job_record.values())
        logging.info(f"Saved job record to {job_record_path}")

        return 
    