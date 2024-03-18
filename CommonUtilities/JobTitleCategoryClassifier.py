"""
When given a Job Title, this class is responsible for loading a CSV and then using it as a map to locate the specific category for this job_title

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
"""


import logging
from dotenv import load_dotenv
import pandas as pd

load_dotenv('.env')

class JobTitleCategoryClassifier:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)  # Ensure logger is set up
        self.logger = logging.getLogger(__name__)  # Get a logger for this class
        self.logger.info(f"{self.__class__.__name__} class initialized")
        self.data_frame = pd.read_csv('CommonUtilities/Configuration/JobCategories.csv')

    def get_job_category(self, job_title):
        """
        Load the CSV Configuration File as a Pandas DataFrame.
        Relative Path = CommonUtilities\Configuration\JobCategories.csv
        Check to see if the Job title is listed in the data frame and then use the job category. 
        Return whatever category has been found. 
        
        If not found, log a message and return category of Unknown.
        """

        # Attempt to find the job title in the DataFrame
        result = self.data_frame[self.data_frame['job_title'].str.lower() == job_title.lower()]
        
        if not result.empty:
            # If found, return the corresponding category
            return result['job_category'].iloc[0]
        else:
            # If not found, log a message and return "Unknown"
            self.logger.info(f"job_title '{job_title}' not found.")
            return "Unknown"