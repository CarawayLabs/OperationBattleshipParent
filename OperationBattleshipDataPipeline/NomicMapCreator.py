"""
Purpose: This script is used to create the Nomic.AI Atlast Map to show all of the jobs. 

High Level Approach
    - After all the jobs have been inserted & enriched (Prio Scripts)
    - Get the list of all jobs from the job_postings table and include the company name
    - Send to Nomic.AI via the Common Utilities Module
    - Insert the URL to the Nomic Table
    
TODO: Once I create the logic to check for active || not active status, I'll want to create that column here and pass to the map. 

"""

import pandas as pd
import logging
import sys
import os
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import numpy as np
import time

import nomic
from nomic import atlas

from operation_battleship_common_utilities.NomicAICaller import NomicAICaller
from operation_battleship_common_utilities.PineConeDatabaseCaller import PineConeDatabaseCaller
from operation_battleship_common_utilities.JobPostingDao import JobPostingDao
from operation_battleship_common_utilities.CompanyDao import CompanyDao
from operation_battleship_common_utilities.NomicDao import NomicDao


load_dotenv()

log_file_path = os.path.join(Path(__file__).parent.absolute(), 'logfile.log')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s',
                    filename=log_file_path,
                    filemode='w')


def main(args):

    # Step 1: Get the Jobs
    allJobsAsDataframe = getAllJobs()
    
    # Step 2: Create the Nomic Map
    nomicAICaller = NomicAICaller()
    mapUrl = nomicAICaller.createMap(allJobsAsDataframe)
    logging.info(f"Nomic Map URL: {mapUrl}")

    nomicDao = NomicDao()
    nomicDao.insertNomicMapUrl(mapUrl)

    return 

def getAllJobs():
    jobPostingDao = JobPostingDao()
    jobsAsDataframe = jobPostingDao.getAllJobs()

    companyDao = CompanyDao()
    companiesAsDataframe = companyDao.get_all_companies()

    # Merge the two dataframes on the 'company_id' column
    jobsWithCompanyName = jobsAsDataframe.merge(companiesAsDataframe[['company_id', 'company_name']], on='company_id', how='left')

    # Select only the necessary columns
    columns_to_keep = [
        'job_description', 
        'company_name', 
        'posting_url', 
        'job_title', 
        'full_posting_description', 
        'is_ai', 
        'job_salary', 
        'job_posting_company_information', 
        'job_posting_date', 
        'job_insertion_date', 
        'job_last_collected_date', 
        'salary_low', 
        'salary_midpoint', 
        'salary_high', 
        'is_genai', 
        'is_ai_justification', 
        'work_location_type', 
        'job_category',
        'job_posting_id'
    ]
    
    jobsWithSelectedColumns = jobsWithCompanyName[columns_to_keep]

    return jobsWithSelectedColumns

if __name__ == "__main__":
    args = {"name": sys.argv[1]} if len(sys.argv) > 1 else {}
    main(args)
