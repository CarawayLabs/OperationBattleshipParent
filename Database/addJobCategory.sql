/*
This SQL Script is used to ADD a new column to the Job Postings Table. We are adding a column called, "job_category"

The current defined categories are: 
- Product_Management
- Data_Science
- Engineerging
- Operations
- Business_Analyst
- Project_Management
- User_Experience
- Business_Development
- Customer_Success
- Marketing
- Sales
- Executive_Role
- Retail
- Food_Services
- Other

*/

ALTER TABLE Job_Postings
ADD COLUMN job_category VARCHAR(25);


