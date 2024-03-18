-- Lets get a list of the unique job titles but also have one example job posting url that we can easily access. 
SELECT job_title, 
       COUNT(*) AS job_title_count, 
       MIN(job_posting_url) AS sample_job_posting_url
FROM job_postings
GROUP BY job_title
ORDER BY job_title_count DESC;
