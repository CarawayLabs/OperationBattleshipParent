"""
In order to get up and running with the most basic recomendation system, we are going to write the simplest approach first. We shall prove that the basic flow our our system works and then begin applying more interesting capabilities and a more thoughtful algorothm for the recomendation. 

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


load_dotenv('.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def convertToEmbedding(resume):
    """
    Converts the resume text string into embedding and then returns this value. 
    """
    nomicAICaller = NomicAICaller()
    embeddedResume = nomicAICaller.embedDocument(resume) 

    return embeddedResume


def getTopNearestJobPostings(embeddedResume, numberOfNeighbors, indexName, namsSpace):

    #Create an instance of PineConeDatabaseCaller and then search for 25 KNN of the input vector
    pineconeApiKey = os.getenv("PINECONE_API_KEY")
    pineConeDatabaseCaller = PineConeDatabaseCaller(pineconeApiKey)
    nearestJobPostings = pineConeDatabaseCaller.query(embeddedResume, numberOfNeighbors, indexName, namsSpace)

    return nearestJobPostings

def getJobPostingDataForNearestNeighbors(listOfNeightbors):

    logging.info(f"Datatype of the listOfNeightbors variable is: {type(listOfNeightbors)}")
    print(listOfNeightbors)

    return

def printResultsToOutputFile(recomendedJobs):

    return 


def returnPdfResumeAsString(resumeRelativeFilePath):
    """
    This function takes in the resume as a PDF is is responsible for opening the file and converting it to a string so it can be returned.

    Args: 
        - resumeRelativeFilePath this is the relative file path to the document that represents the applican'ts resume. Its expected to be in PDF Form. 

    Return Value: A Python String that represents 
    """

    resumeAsString = extract_text(resumeRelativeFilePath)

    return resumeAsString


def main():
    
    #Variables that are used for this script: 
    indexName = "job-postings" 
    namsSpace = "full_posting_description"
    resumeRelativeFilePath = "Resumes\\MatthewCarawayResume.pdf"
    
    resume = returnPdfResumeAsString(resumeRelativeFilePath)

    embeddedResume = convertToEmbedding(resume)

    listOf25Neightbors = getTopNearestJobPostings(embeddedResume, 25, indexName, namsSpace )

    recomendedJobs = getJobPostingDataForNearestNeighbors(listOf25Neightbors)

    #printResultsToOutputFile(recomendedJobs)
    printResultsToOutputFile(listOf25Neightbors)

    return 


if __name__ == "__main__":
    logging.info(f"Hello World - Resume Recomendation Script has started.")
    main()