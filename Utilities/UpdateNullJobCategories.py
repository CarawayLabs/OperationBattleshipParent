"""
Purpose

As we've built the application, we've discovered several valuable additions to the datamodel. Of particular interest for this notebook is the Job Category Column in the Job Postings Table. Because a Product Manager Role is written 10 different ways, we need a way to come up with a categorical description that seprates out roles that are very different from each other. 

Example Categories:
- Product_Management
- Data_Science
- Engineerging
- Operations
- Business_Analyst
- Project_Management
- User_Experience
- Business_Development
- Customer_Success
- Marketing
- Sales
- Executive_Role
- Retail
- Food_Services
- Other

This script is intended to apply the job category to the jobs that we've already post processed in the JobPostingDataEnrichment Script. We will do this by quering the job_postings table and find the records where is_ai is not null and job_category is null. 

We will then iterate through the collection and apply the job category and finally, we will insert the record into the db. 

"""

import os
import sys
import time
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
from CommonUtilities.JobTitleCategoryClassifier import JobTitleCategoryClassifier


def dropUnnecessaryColumns(df):
     """
     The dataframe is larger than required for this script. To save on memory and also avoid logic to handle NaN values, we can drop the unnecessary columns. 

     """
     
     df.drop(columns=['full_posting_description', 'salary_low', 'salary_midpoint', 'salary_high'], inplace=True)
     df.drop(columns=['posting_url', 'posting_source_id', 'posting_source', 'job_last_collected_date'], inplace=True)
     df.drop(columns=['job_posting_date', 'work_location_type', 'is_ai_justification', 'job_insertion_date'], inplace=True)
     return df


jobPostingDao = JobPostingDao()
uncategorizedJobs = jobPostingDao.getUncategorizedJobs()

uncategorizedJobs = dropUnnecessaryColumns(uncategorizedJobs)

totalRecords = 0
errors = 0
for index, job_record in uncategorizedJobs.iterrows():
        job_start_time = time.time()
        try:
            
            jobTitleCategoryClassifier = JobTitleCategoryClassifier()
            job_record["job_category"] = jobTitleCategoryClassifier.get_job_category(job_record["job_title"])
            logging.info(f"Job Category has been set to: {job_record['job_category']} ")
            
            jobPostingDao = JobPostingDao()
            jobPostingDao.update_job_posting(job_record)

            logging.info(f"Finished updating the job category a single job. Job Title = {job_record['job_title']} ")
            totalRecords += 1

        except Exception as e:
            # Log the exception and skip to the next job record
            logging.error(f"Error processing job record {job_record['job_title']}: {e}")
            errors = errors + 1

        finally:
            job_end_time = time.time()  # Capture end time
            duration_ms = (job_end_time - job_start_time) * 1000  # Calculate duration in milliseconds

            # These logging statements will execute whether or not an exception occurred
            logging.info(f"We have categorized {totalRecords} total jobs")
            logging.info(f"We have observed {errors} total errors")
            logging.info(f"There are {uncategorizedJobs.shape[0]} total jobs to be processed")
            logging.info(f"Last record to update took {duration_ms:.2f} milliseconds")
