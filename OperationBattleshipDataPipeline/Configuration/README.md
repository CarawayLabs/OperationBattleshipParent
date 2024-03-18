# Purpose

The files in this directory are using as configuration for different parts of the application. Obviosly, this avoids hard coding information into the code and allows for increased extensibility. As the project grows, we will add additional config files and also config file types. 

## Job Roles JSON Files
These files are used by the ApyfyJobsCaller Script. The file contains a collection of different ways we can search LinkedIn to find roles that are of that type. For instance, there's a dozen different ways that we've seen the Product Manager Job Title. 

- productManagerJobTitles.json 
    - List of different job titles that help us find Product Manager Jobs. These range from IC to CEO Level roles. It also ranges in specialty. We have general PM roles and also AI roles, Growth roles too! 
- softwareEngineerJobTitles.json
    - List of different job titles that help us find Software Engineer Jobs. This includes different levels of the role and also specialties like Machine Learning Engineer. 
- virtualRealityJobTitlesComplete.json
    - List of different job titles that help us find all jobs related to Virtual Reality. This is a big set and will find jobs that are beyond Product - Technology Roles. 
- virtualRealityJobTitlesConcise.json
    - List of different job titles that help us find Virtual Reality Jobs. The concise set is focused on roles related to Product - Technology. 