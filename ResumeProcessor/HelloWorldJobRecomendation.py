"""
In order to get up and running with the most basic recomendation system, we are going to write the simplest approach first. We shall prove that the basic flow for our our system works and then begin applying more interesting capabilities and a more thoughtful algorothm for the recomendation in future scripts. 

Intended steps for the Hello World:
- Process a PDF File
- Call the LLM and get:
    - Job Title
    - Skills
    - Keywords

- Convert the PDF Document to an embedding using the Nomic Embedding Model
- Query the Vector DB for the list of top 30 KNN via Cosine Search in the index of "Full Posting Description"
- Query Postgres and get the job titles, is_ai, posting_url, company_name and job_posting_id
- Save the results to a CSV file for easy reading. 
"""



import logging
import sys
import os
import pandas as pd
from pathlib import Path
from pdfminer.high_level import extract_text
from dotenv import load_dotenv

# Get the directory of the script being run:
current_script_path = os.path.abspath(__file__)

# Get the parent directory of the current script:
parent_directory = os.path.dirname(os.path.dirname(current_script_path))

# Add the parent directory to the sys.path:
if parent_directory not in sys.path:
    sys.path.append(parent_directory)

from CommonUtilities.NomicAICaller import NomicAICaller
from CommonUtilities.PineConeDatabaseCaller import PineConeDatabaseCaller
from CommonUtilities.JobPostingDao import JobPostingDao


load_dotenv('.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def convertPineconeResultsToDataframe(listOfNeightbors):

    data = []
    for match in listOfNeightbors['matches']:
        entry = {
            'job_id': match['id'],
            'job_category': match['metadata']['job_category'],
            'job_posting_date': match['metadata']['job_posting_date'],
            'score': match['score']
        }
        data.append(entry)

    # Creating the dataframe
    df = pd.DataFrame(data)

    return df


def convertToEmbedding(resume):
    """
    Converts the resume text string into embedding and then returns this value. 
    """
    nomicAICaller = NomicAICaller()
    embeddedResume = nomicAICaller.embedDocument(resume) 

    return embeddedResume


def getTopNearestNeighborsInNamespace(embeddedResume, numberOfNeighbors, indexName, namsSpace):

    #Create an instance of PineConeDatabaseCaller and then search for Top N KNN of the input vector
    pineconeApiKey = os.getenv("PINECONE_API_KEY")
    pineConeDatabaseCaller = PineConeDatabaseCaller(pineconeApiKey)
    nearestJobPostings = pineConeDatabaseCaller.query(embeddedResume[0], numberOfNeighbors, indexName, namsSpace)

    return nearestJobPostings


def getJobPostingDataForNearestNeighbors(listOfNeightbors):

    logging.debug(f"Datatype of the listOfNeightbors variable is: {type(listOfNeightbors)}")
    #print(listOfNeightbors)

    pineconeResultsAsDataframe = convertPineconeResultsToDataframe(listOfNeightbors)

    jobPostingDao = JobPostingDao()
    jobs = jobPostingDao.getjobsFromListOfJobsIds(pineconeResultsAsDataframe)
    
    return jobs


def printResultsToOutputFile(recommendedJobs):
    """
    Persists the Pandas Dataframe of recomended jobs to a csv file on disk. 

    Args:
        recommendedJobs: Dataframe of jobs

    Return Value: 
        none

    """
    if not isinstance(recommendedJobs, pd.DataFrame):
        raise ValueError("The recommendedJobs argument must be a pandas DataFrame.")

    # Define the path and name of the file where you want to save the DataFrame
    output_file_path = 'recommended_jobs.csv'
    
    # Save the DataFrame to a CSV file
    recommendedJobs.to_csv(output_file_path, index=False)

    logging.debug(f"Recommended jobs have been saved to {output_file_path}.") 

    return 


def returnPdfResumeAsString(resumeRelativeFilePath):
    """
    This function takes in the resume as a PDF and is responsible for opening the file and converting it to a string so it can be returned.

    Args: 
        - resumeRelativeFilePath this is the relative file path to the document that represents the applican'ts resume. Its expected to be in PDF Form. 

    Return Value: A Python String that represents 
    """

    resumeAsString = extract_text(resumeRelativeFilePath)

    return resumeAsString


def main():
    
    #Variables that are used for this script: 
    indexName = "job-postings" 
    namsSpace = "full-posting-description"
    resumeRelativeFilePath = "Resumes\\MatthewCarawayResume.pdf"
    
    resume = returnPdfResumeAsString(resumeRelativeFilePath)

    embeddedResume = convertToEmbedding(resume)

    listOfNeightbors = getTopNearestNeighborsInNamespace(embeddedResume, 250, indexName, namsSpace )

    recomendedJobs = getJobPostingDataForNearestNeighbors(listOfNeightbors)

    printResultsToOutputFile(recomendedJobs)

    return 


if __name__ == "__main__":
    logging.info(f"Hello World - Resume Recomendation Script has started.")
    main()