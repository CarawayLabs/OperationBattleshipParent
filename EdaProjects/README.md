# EDA Backlog
As we build out this application, we will consider the opporunities to explore the data further. Down beloe in this READEME, I've listed some ideas for Exploratory Data Analysis that I might conduct in order to learn more about the data and be better suited to buid more advanced features in the application. 

- The key motivator for this project is that I assume ML Product Managers will make more than traditional Product Managers. We can test that hypothesis in the data by measuring the mid point of the salary and compare that from PM Jobs where is_ai = true vs jobs where this is false.
- Time series of the amount of jobs posted each day. 
    This will be flawed because we' modified our search paramters and also changed the frequency that we query for jobs. But non-the-less, it will still be interesting to see what insights we can gain from this. 
- Pie chart of the different job title categories
    I've biased the search parameters to be roles that are similar to Product Manager Job titles. However, we've got some Job Title Categories that are not Product. Lets explore these further and see what we can learn. 
- What companies have created the most jobs
    - Are there companies that have the most jobs? Do we want to work for them?
- Whats the distribution of word count (length) of each job posting?
    - As we've built the application, I've take a couple ad-hoc looks at the job postings. It appears that the low quality jobs and also the contractor jobs are often short in length. Lets see what we can learn about the length of a Job Posting. 


# ML Techniques 
In addition to basic EDA, we will have a backlog of different ML project to potentially apply to this dataset. 

- Similarity Measurement
    - CoSine Similarity for Resumes to Job Descriptions
    - Other distance and relationship metrics

- K Means Clustering
    Can we use unsupervised learning techniques to learn more about this dataset?

- Predicting the Job Category using ML Techniques
    I wonder if I can embed the Job Title string and then apply some form of ML to predict the category of the job. I don't actually know. But it will be worth attempting at some point in the future. 

- Preidcting the Job Category using Cosine Search. 
    Given a job title that is unknown, can we query for the top 25 KNN and then sort by Job Category and assign that one?


