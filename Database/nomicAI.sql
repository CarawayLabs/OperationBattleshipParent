SELECT 
    job_postings.company_id, 
    job_postings.job_posting_id, 
    job_description, 
    c.company_name, 
    job_posting_id, 
    posting_url,  
    job_title, 
    full_posting_description, 
    is_ai, 
    job_salary, 
    job_posting_company_information, 
    job_posting_date, 
    job_insertion_date, 
    job_last_collected_date, 
    job_active, 
    salary_midpoint, 
    is_genai, 
    work_location_type
FROM public.job_postings
INNER JOIN companies c ON job_postings.company_id = c.company_id;