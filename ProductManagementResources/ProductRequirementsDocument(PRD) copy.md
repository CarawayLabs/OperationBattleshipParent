# Product Requirements Document (PRD) for Operation Battleship from Caraway Labs

## 1. Introduction

### Purpose of the Document
This document outlines the product requirements for Operation Battleship MVP launch from Caraway Labs. This is an application designed to improve the job hunt experience for Product Managers. The information contained within this PRD serves as a guide to understand how we got here and how we intend to help our users achieve a more desirable job search experience. The document includes:
- Product Vision
- User Personas
- The research that helped us validate this problem.
- Defined outcomes
- Implementation Details

### TLDR: 
Users can email, [findMyNextJob@CarawayLabs.com](mailto:findMyNextJob@CarawayLabs.com) with their resume attached and we will send back a customized email with the top jobs recomended for them. We will also deliver a series of reports that are specific to the top five jobs in their recomendation. Finally, we will link them a map so that they can explore all of the jobs available to. Similar jobs are clustered together so users can find roles that are similar to ones they are interested in. This map is powered by Atlast from Nomic.AI

### Background
With a rise in the competition of the labor market, optimizing your time as a Product Manager has become even more important than before. 

#### Market Opportunity
There's a clear absence of job search tools that job seekers **_enjoy_** using. Instead of being the **_customer_**, job seekers are often the **_product_** that is sold to other parties. We intend to fill this gap by delivering Operation Battleship for Product Managers who are seeking new job opportunities.  


#### Customer Problem
As a Product Manager, when they open LinkedIn and search for the latest jobs, the experience is frustrating and clearly not optimized for their role as a job seeker. The user is faced with a search window that only presents 25 jobs at a time. And even more frustrating, the first several pages are always promoted job postings that appear first because the employer paid money to appear at the top. There's not an easy way to see which jobs are most relevant to them. Nor is there a capability that allows the job seeker to zoom out to a 10,000 foot view of the Job Market and see all available roles and understand how they might be related to each other. 


## 2. Product Overview

### Product Vision
- In a world where top-tier talent often misses out on the opportunities that match their skills and aspirations, we aim to be the intelligent sonar of the job market. We strive to lift the fog of war, providing a comprehensive, real-time panorama of Product Manager job openings across the U.S. economy. Our platform equips Product Managers with the insights they need to pinpoint roles that not only align with their career goals but also resonate with their values. We are committed to making the job search as efficient, transparent, and rewarding as possible, so that the best in the industry can effortlessly find their perfect fit, driving both individual and organizational excellence.

### Product Objectives
- Key objectives this product aims to achieve, including business and user objectives.

### Target Audience
- Product Managers who are seeking their next job opportunity. 


### Key Hypothesis
We beleieve that by providing innovative and novel search tools that allow Product Managers to find roles most relevant to them AND also explore the job market, they will have a more satisfying and less frustrating job search experience. Its is our belief that an improved search experience will allow a Product Manager to 


### Outcomes to achieve
- Product Managers report they are able to find fulfilling jobs that align with their skillset and career aspirations. 
    - We don't intend to just puke random jobs to the user. We want to produce the RIGHT jobs for them. 
- Product Managers can accomplish their job search with more knowledge of the roles available, and also adjacent roles. 


## 3. Prior Research and Evidence
Our personal experience and interviews of other Product Managers during the problem validation phase was key in helping us find the right solution to test for our first MVP. In addition to interviews, we leveraged Product Playbooks from Learning Loop. You can read more about them at the following link: [Learning Loop - Product Playbooks](https://learningloop.io/playbooks/)

### 


## 4. Scope

### Comment on Lean Methods
In the spirit of "chasing progress over perfection", we've paired down this product for our first release. We believe we can validate our algorithm and provide meanfingful value to our users if we deliver the job recomendations via an email. This allows us to avoid the time and complexity of building a fully functional Web Front End for the MVP. 


### In Scope
- Clearly outline what is included in the product's scope.

### Out of Scope
- Specify what is excluded from the current product scope.
- The ability for companies to post jobs

## 5. Assumptions and Dependencies

| Assumptions | Dependencies |
|-------------|--------------|
| Assumption 1 | Dependency 1 |
| Assumption 2 | Dependency 2 |

## 6. Requirements

### Functional Requirements
- Detailed description of product functionalities and features.

#### User Stories & Acceptance Criteria
- **User Story:** As a [Prooduct Manager], I want [an ordered list of the top recomended jobs for me] so that [I can optimize my job search and quickly find the jobs that are aligned with my experience, skillset and career goals].
  - **Acceptance Criteria:**
    - Users can send their resume to [findMyNextJob@CarawayLabs.com](mailto:findMyNextJob@CarawayLabs.com)
    - The system will respond back with a list of the recomended jobs for the user's provided resume. 
    - The user can email a modified resume and the recomendation engine will trigger off of this updated resume.

- **User Story:** As a [Prooduct Manager], I want [a tailored report] so that [reason].
  - **Acceptance Criteria:**
    - For the top five jobs, users will get a custom report that allows them to have additional insights and inteligence about their resume & these specific jobs.
    - The custom report will be included in the email returned to users. 

- **User Story:** As a [Prooduct Manager], I want [] so that [reason].
  - **Acceptance Criteria:**
    - Criterion 1
    - Criterion 2

- **User Story:** As a [Prooduct Manager], I want [relevant information on the evolving job market] so that [I can see newly posted AI Jobs, even if they are not in the top recomendation list].
  - **Acceptance Criteria:**
    - Email will include recently posted jobs where is_ai is set to true. These will be sorted by posting date and salary midpoint will be a tie breaker. 
    - Email will include recently posted jobs where is_GenAi is set to true. These will be sorted by posting date and salary midpoint will be a tie breaker. 

### Non-Functional Requirements
- The email response back to the user is not required to be real time. As long as the user recieves an email of recomended jobs within 24 hours, this will be sufficient for MVP. 
- Users that subscribe to daily updates, will get the emails at 6AM Mountain each day. 

## 7. User Interface and Design

### UI Requirements
- Detailed UI requirements, including wireframes and design mockups.

### Design Principles
- Key design principles the product should adhere to.

## 8. Technical Requirements

### Application of AI
Operation Battleship relies on the use of AI in several key areas:
1. ChatGPT 3.5 
Used to process each job posting and create inteligence, structure and metadata. This includes things like:
    - Summarizing the Employer Information in the job posting. 
    - Summarizing the information that is specific to the role being hired for. 
    - Determining if the job relates to AI and gives a justifcation for the boolean setting
    - Determining if the job related to Generative AI and gives a justifcation for the boolean setting
    - Finds salary information if its written in the job posting. 
    - Determines if the role is in-person, hybrid or remote. 
    - Identified key qualifications the candidate must meet in order to be succesful. 
2. Nomic.AI Document Embedding 
 Allows us to convert our unstructured text into embeddings and be upserted into the Pinecone Vector DB. 
    - Embeddings are the backbone of the recomendation engine. 

3. Atlas from Nomic.AI
    - Using a high scale, two-dimensional scatter plot, users can explore the whole job market. 
    - We've embedded the whole job posting (Employer & Job Information) so that 
    - The embedded data is represented on the map using a modified TSNE Algorithm developed by Nomic. 
    - Inspiration for the use of Nomic.AI's Atlast Product was found from a Scientific Paper that explored the evolution of Biomedical Research. 
        - [The landscape of biomedical research](https://static.nomic.ai/pubmed.html)
        - Link to published paper on Biorxiv: [Biorxiv: The landscape of biomedical research](https://www.biorxiv.org/content/10.1101/2023.04.10.536208v4)


4. ChatGPT 3.5
Used to generate the custom reports send to the users each dat


5. **Future** Categorizing job category using either a linear classification model or semantic similary. 

### Architecture
We deployed our application using a hybrid cloud approach. Portions of the product live on-prem because they do not require high uptime and it allows us to save on infrastructure costs. Here's a short breakdown of the major technologies that are used in the application
- Postgres RDBMS hosted on Digital Ocean
- Pinecone Vector DB
- Fast API REST Microservices hosted on Digital Ocean
- Google Workspace to host email services.
- Google Cloud Platform to alert on new emails in the inbox at [findMyNextJob@CarawayLabs.com](mailto:findMyNextJob@CarawayLabs.com)
- Apify to source the jobs
- Datapipeline written in Python and runs locally, on-prem. 
 
### Data Model
- PostGres RDBMS
    - Version one of the product includes information about Companies, Jobs and  .
- Pinecone Vector DB


### Security Requirements
- Security was not a top concern for this first launch. No major security requirements were provided. 

## 9. Milestones and Timeline

### Development Milestones
- List of major milestones in the development process:
    - Jobs available in unstructured form in the PostGres DB
    - Jobs exported to Nomic for manual analysis

### Timeline
High-level timeline for development and launch.
    - Our goal for Operation Battleship was to go from vision to reality in roughly a 90 day window.
    - First 14 Days - User Research and problem validation
    - First 30 Days - Design relational datamodel and first iteration of data pipeline. 
    - Second 30 Days -  

## 10. Risks and Mitigation

| Risks | Mitigation Strategies |
|-------|-----------------------|
| Risk 1 | Mitigation Strategy 1 |
| Risk 2 | Mitigation Strategy 2 |

## 11. Appendices

### Glossary
- Definitions of terms and acronyms used in the document.

### References
- Playbook of lean methods and experiments 
- Any references or external documents consulted.

