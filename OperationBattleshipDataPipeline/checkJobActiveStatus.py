"""
This script is responsible for determining the status of a job and updating the selection so that we correctly mark jobs as inactive. 
In order to reduce wasted calls, we will assume a job is active for three weeks before we start checking the status. 

The basic logic is that the file will query the url
- If a non-200 code comes back, we assume inactive. 
- If a redirect occurs, we assume the job is inactive.
- If the job posting says, "no longer active", we assume the job is inactive. 
- Else, we assume the job is active and we do nothing. 

When a job is determined to be inactive, we go update the DB with this information. 

"""

import requests
from bs4 import BeautifulSoup



import random
import string
import datetime
import uuid
import time
import sys
import logging
import pandas as pd
import os
import json
import shutil
from dotenv import load_dotenv
from datetime import datetime

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




# Assume you have a list of URLs stored in job_urls.txt
with open('job_urls.txt', 'r') as file:
    job_urls = file.readlines()

def check_job_active(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Customize this condition based on your observation of active jobs
            return "Apply Now" in response.text
        else:
            return False
    except Exception as e:
        print(f"Error checking {url}: {e}")
        return False

for job_url in job_urls:
    job_url = job_url.strip()  # Remove any leading/trailing whitespace
    is_active = check_job_active(job_url)
    print(f"Job URL: {job_url} is {'active' if is_active else 'not active'}")



def getUrlsThatAreCurrentlyActive():

    return 

def checkJobStatusAndUpdateIfInactive(activeJobs):

    return

def main(args):

    activeJobs = getUrlsThatAreCurrentlyActive()
    checkJobStatusAndUpdateIfInactive(activeJobs)

    return


if __name__ == "__main__":
    import sys
    # Convert command line arguments to a dictionary or any suitable format
    args = {"name": sys.argv[1]} if len(sys.argv) > 1 else {}
    main(args)