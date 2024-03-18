/*
This SQL Select statement is used to build the CSV that we will upload to the Nomic.AI Atlas. 
We've excluded some fields from the Job Postings and Companies DB that contain the IDs and other fields that won't provide meaning and value to users when they will view it on the 2D Scatter Plot. 

*/


SELECT 
    job_description, 
    c.company_name, 
    posting_url, 
    job_title, 
    full_posting_description, 
    is_ai, 
    job_salary, 
    job_posting_company_information, 
    job_posting_date, 
    job_insertion_date, 
    job_last_collected_date, 
    salary_low, 
    salary_midpoint, 
    salary_high, 
    is_genai, 
    is_ai_justification, 
    work_location_type, 
    job_category
FROM public.job_postings
INNER JOIN companies c ON job_postings.company_id = c.company_id;