# Purpose: 
As we've iterated on the product, we've found new updates to the datamodel and also implemented a Vector DB. We needed to write a couple simple scripts that populate the null or missing values. Our Data Pipeline is then updated to insert the correct values into the system moving forward. 

## Scripts in this directory: 
- PopulatePineConeVectorDB
    - Queries all of the AI and Product Manager jobs and then inserts them into the Pincecone Vector DB. This is requried because we had built the Vector Database and Semantic Search Capabilities in later iterations of the project. Therefore, we have a lot of records in the PostGres DB that were not present in the Vector DB. 

- UpdateNullJobCategories
    - As we built the application, it became really obvious that Product Manager Roles are written in many different ways. We added a new column to the datamodel for "Job Category". This script is used to map the Job Title for a Job Posting into a pre-defined list of categories for our system. Given that we had thousands of records in the DB with null values for Job Category, we needed to execute this script once to fill in all the missing values. 