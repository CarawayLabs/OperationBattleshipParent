# Operation Battleship Data Pipeline
This folder contains the python scripts and any associated configuration files that ingest, process and enrich the data used for the application. 
- Initial MVP focus is on Jobs. 
- Further enrichment and inteligence about comanpies is provided later. 


### Contents
To save on cloud computing costs, we've built these scripts with the intention to run them locally. Decisions about where to store the Raw Collections will need to be made in order for us to move this to the cloud. 

#### Python Scripts:
- OperationBattleshipDataPipeline\ApifyJobCallerRunner.py
    - This script is used to trigger the actual searching and locating of the jobs. We can target by job title or by company name. 
- OperationBattleshipDataPipeline\JobPostingProcessor.py
    - The script is reponsible for inserting new Job Posting records into the database. It pulls from the Raw Collections Folder and then inserts into the DB. For future use and potential debugging, the processed records are storied in the Processed Collections Folder.  
- OperationBattleshipDataPipeline\JobPostingDataEnrichment.py
    - This script allows us to increase the information that we have when only givin the Job Description. We parse company info, salary and AI information, others too!

#### Configuration:
- OperationBattleshipDataPipeline\Configuration
- OperationBattleshipDataPipeline\LlmTemplates
- OperationBattleshipDataPipeline\ProcessedCollections
- OperationBattleshipDataPipeline\RawCollections

