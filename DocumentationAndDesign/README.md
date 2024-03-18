# Overview
This readme is intended to give a short introduction to the technical approach we've taken for this project. I'll be writing comments in this README, adding files to this directory and even just giving a link to my online Google Drive where a lot of collateral is also stored. 

## System Design
Please see this link to view a version of our end state that we drafted in late 2023. 

Please see this link to view a diagram of how our MVP is constructed. This approach uses email as a channel to deliver job recomendations to our users. 

# Vendor Selection
The application requires the use of several different technologies. I wrote about the comparison and decisions in this Word Doc:
[Choosing the Vendors](https://docs.google.com/document/d/1BYRZwORqREC37Ubvum29JXfbbOKmvNFU3Jxdc50zXqE/edit?usp=sharing)


## Cloud Vendor Selection
I've considered hosting the application on several providers. AWS, Google Gloud, Azure and also Digital Ocean. In the near term, Ive elected to use Digital Ocean because of its low cost and simplcity. 


## Relational Database
The backbone of our entire system is the way that we've stored our data at rest. We've elected to use a PostGres DB to store information about these things:
- Companies
- Job Postings
    - Skills listed in Job Postings
    - Key words listed in Job Postings
- Job Candidates
- Jobs that a Job Candidate is interested in

## Data Pipeline
Each night our pipeline is triggered and runs these scripts
- OperationBattleshipDataPipeline\CombinedJobProcessorRunner.py
    This script is used to control the flow and kicks off each script in series. When we optimize our processing times, we will update this script so that we can run a few instances of the Job Processors in paralell. 
- OperationBattleshipDataPipeline\ApifyJobCallerRunner.py
    When given no args, this script will call the Apify Platform and get jobs that are AI Product Manager and Product Manager Jobs that have been posted in the last 24 hours. Alternatively, you can pass in a filename that includes a collection of different Job Titles to query for. This is intended to create flexibility and allows our application to expand well beyond just PM Jobs. 
- OperationBattleshipDataPipeline\JobPostingProcessor.py
    Once Apify has processed the jobs, we open a collection of JSON Files and parse these into the PostGres DB. This script is pretty straightforward and is really just focused on conerting the JSON File to entries in the PostGres DB. 
- OperationBattleshipDataPipeline\JobPostingDataEnrichment.py
    We use the LLM to parse the full job description and apply some metadata and then we save this information to the Job Postings Table. This file is the first application of an LLM and AI Technology in our application. Honestly, there really isn't another reliable route to summarizing a job description and adding metadata other than using an LLM. Right now we are using ChatGPT. In the future, I'd like to explore the use of a local LLM to reduce the cost. 
