"""
This python script is reponsible for determining if a job is still active or now. 

- Get the list of all jobs in the DB where job status = active
- Iterate through this list 
- Call the Apify Job Crawler for each job posting url
- If a non-200 code comes back, then we set active = false
- We then parse the return object and we are looking for information that the job is not accepting applicants any more. We will then set it to false
- If the return JSON contains active information, we do nothing and move on to the next element in the collection. 



"""



import os
import inspect
import json
import sys
import logging
import pandas as pd
from dotenv import load_dotenv

# Get the directory of the script being run:
current_script_path = os.path.abspath(__file__)

# Get the parent directory of the current script:
parent_directory = os.path.dirname(os.path.dirname(current_script_path))

# Add the parent directory to the sys.path:
if parent_directory not in sys.path:
    sys.path.append(parent_directory)



from CommonUtilities.JobPostingDao import JobPostingDao
from CommonUtilities.ApifyJobsCaller import ApifyJobsCaller


load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def getActiveJobs():

    jobPostingDao = JobPostingDao()
    jobPostingDao.getActiveJobs()

    return

def determineCurrentJobStatus():

    return

def main(args):

    func_name = inspect.currentframe().f_code.co_name
    logging.info(f"We have entered {func_name}")

    getActiveJobs()

    determineCurrentJobStatus()


    return 


if __name__ == "__main__":
    import sys
    # Convert command line arguments to a dictionary or any suitable format
    args = {"name": sys.argv[1]} if len(sys.argv) > 1 else {}
    main(args)