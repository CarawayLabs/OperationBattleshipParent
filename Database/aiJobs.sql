/*
This SQL Query is used so we can see the AI Jobs and the basic metadata associated with them. 
We've excluded two companies because the usually have low quality job postings. 
*/

SELECT 
    job_title,
	salary_midpoint,
	c.company_name, 
	job_posting_date,
	posting_url, 
    job_description, 
    full_posting_description,
	job_category,
    is_ai, 
    job_salary, 
    job_posting_company_information,  
    salary_low, 
    salary_high, 
    city, 
    state, 
    is_genai, 
    is_ai_justification, 
    work_location_type
FROM public.job_postings
INNER JOIN companies c ON job_postings.company_id = c.company_id
where is_ai is true
and company_name != 'SimplyApply' 
and company_name != 'Jobot' 
and company_name != 'Cheez'
order by job_posting_date desc;
