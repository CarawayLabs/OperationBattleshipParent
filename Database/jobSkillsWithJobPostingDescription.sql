/*
This SQL Query will return a list of all records in the Job Skills Table and use a join function to get additional data from two other tables
From Job Postings: Job title, Job Posting Description 

From Companies Table: Company Name. 


The intention for this data is that we will plot the Job Skills in the Nomic Map and try to explore how different skills are clustered. 
We hypothesize that by plotting the job skills, we can overlay a candidates job skills and then find K-Nearest Neighbors to seek other jobs that require similar skills. 

*/

SELECT
    js.unique_id,
    js.item AS skill,
    jp.job_posting_id,
    jp.job_title,
    jp.full_posting_description,
	jp.posting_url,
    c.company_id,
    c.company_name
FROM
    job_skills js
INNER JOIN job_postings jp ON js.job_posting_id = jp.job_posting_id
INNER JOIN companies c ON jp.company_id = c.company_id;
