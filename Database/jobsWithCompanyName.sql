/*
This SQL Script is used to pull all the jobs and the meta data about each job record. We join on the companies table in order to get the company name. 
For the early phases of this product, we manually uplaod this data as a CSV to Nomic. 
Atlas from Nomic.AI allows us to explore the jobs using a two dimensional scatter plot view. 
We believe this is beneficial becaue 

*/

SELECT 
    job_postings.company_id, 
    job_postings.job_posting_id, 
    job_description, 
    c.company_name, 
    job_posting_id, 
    posting_url, 
    posting_source, 
    posting_source_id, 
    job_title, 
    full_posting_description, 
    is_ai, 
    job_salary, 
    job_posting_company_information, 
    job_posting_date, 
    job_insertion_date, 
    job_last_collected_date, 
    job_active, 
    salary_low, 
    salary_midpoint, 
    salary_high, 
    city, 
    state, 
    is_genai, 
    job_skills, 
    is_ai_justification, 
    work_location_type, 
    job_category
FROM public.job_postings
INNER JOIN companies c ON job_postings.company_id = c.company_id;
