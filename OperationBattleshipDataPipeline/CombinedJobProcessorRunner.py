"""
Our data pipeline is built in a sequential manner. We have several scripts that are intended to run in a specific order. This Python Script will be used to kick off each script so that this can be done in a single file with just one command. 

The relative path to each script is provided below. We also give a short description of its purpose. 

1: OperationBattleshipDataPipeline\ApifyJobCallerRunner.py
    This is the first script that runs and is used to gather Job Postings from LinkedIn. It used the Apify Job Crawler. 
    When given zero args, it will default to finding AI PM Jobs that have been posted in the last day. 
    If we want to find other jobs, we have to pass in the name of the Jobs JSON File & a time window. 

2: OperationBattleshipDataPipeline\JobPostingProcessor.py
    This script will process all the jobs in the Raw Collections folder and insert them into the DB. 

3: OperationBattleshipDataPipeline\JobPostingDataEnrichment.py
    This script is used to add additional meta data about each job record. In order to add structure and additional information about each job, we call the LLM to help provide this inteligence. 
    In the future, we will also be creating embeddings from some of the text fields and inserting into Pinecode for allowing Vector Searching. 

"""

import subprocess
import sys
import inspect
import logging

def execute_script(script_path, args=[]):
    """
    Executes a Python script located at 'script_path' with optional arguments 'args'.
    """
    subprocess.run(["python", script_path] + args, check=True)

def main(custom_args={}):

    func_name = inspect.currentframe().f_code.co_name
    logging.info(f"We have entered {func_name}")

    # Paths to the scripts
    scripts = [
        ("OperationBattleshipDataPipeline/ApifyJobCallerRunner.py", custom_args.get("job_args", [])),
        ("OperationBattleshipDataPipeline/JobPostingProcessor.py", []),
        ("OperationBattleshipDataPipeline/JobPostingDataEnrichment.py", [])
    ]

    # Execute each script in sequence
    for script_path, args in scripts:
        try:
            logging.info(f"Executing: {script_path} with args: {args}")
            execute_script(script_path, args)
        except subprocess.CalledProcessError as e:
            logging.info(f"Failed to execute {script_path} with error: {e}")
            break  # Stop execution if any script fails

if __name__ == "__main__":
    # Parse command line arguments into a dictionary for custom job search
    # Example usage: python script_name.py --jobs "AI PM Jobs" --window "7 days"
    # This expects that the first script can handle these named arguments.
    custom_args = {}
    if len(sys.argv) > 1:
        custom_args["job_args"] = sys.argv[1:]
    main(custom_args)