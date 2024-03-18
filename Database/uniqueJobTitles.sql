-- Lets get the list of all unique job titles in the DB. 
SELECT job_title, COUNT(*) AS job_title_count
FROM job_postings
GROUP BY job_title
ORDER BY job_title_count DESC;
