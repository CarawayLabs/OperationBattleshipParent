# Common Utilities
Operation Battleship is spread among several different repositories. We've got the data pipeline and also the microservices deployed to Digital Ocean that provide the job recomendations for the job applicants. In order to follow basic engineering practices and support modular code, we have split out some of the common and shared classes into their own repo. 

## Files and Classes
Here's a quick list of the files that are in the Common Utilities and a short description for each file.

- ApifyJobsCaller.py
    This file is the one that interacts directly with the Apify SDK. No other instances of the Apify dependency should exist outside this Python class

- CandidateRequirementsDao.py
    This Python script is a data access object (DAO) for managing candidate requirements data in a PostgreSQL database. It includes a method for inserting multiple records from a DataFrame into the Candidate_Requirements table in the database. The script uses environment variables for database connection parameters, ensuring secure handling of sensitive data.

- CompanyDao.py
    This Python script is a data access object (DAO) for managing company data in a PostgreSQL database. It includes methods for checking if a company exists in the database, retrieving a company’s UUID by its LinkedIn URL, and inserting new company data from a DataFrame into the Companies table.

- FailureLogger.py
    This Python script is designed to handle and log instances where a Language Learning Model (LLM) fails to generate a well-formed JSON response. It saves the LLM response and the associated job title to disk for later analysis, aiding in the identification of potential issues with job postings.

- GenaricDatabaseDao.py
    This script is intended to be the only class that actually calls the PostGres DB. All other DAO Classes will reference this Class. 

- GeographyHelper.py
    This Python script, GeographyHelper, is designed to parse and extract city and state information from a given string. It uses regular expressions to match patterns and returns the results as a DataFrame, making it useful for processing and standardizing geographical data.

- JobKeyWordsDao.py
    This Python script defines a class JobKeyWordsDao that connects to a PostgreSQL database and inserts job keywords from a pandas DataFrame into the ‘Job_Keywords’ table. It uses environment variables for secure database access and includes logging for execution tracking.

- JobPostingDao.py

- JobTitleCategoryClassifier.py

- OpenAICaller.py