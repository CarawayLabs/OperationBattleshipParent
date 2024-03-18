# Vector Database for Operation Battleship

We've explored several different options for deciding which Vector Database to use for this project. The primary factors that influenced decision making are:
    1: Ease of use: We want to quickly get up and running. We are willing to self-host if the overhead is reasonable. And we want to interact with the data with a degree of ease. 
    2: Cost: This project is currently low scale and merely a POC. We wanted to keep the monthly cost low in order to manage budget. 

### Top Options that we explored:
- Microsoft Cosmos
- Croma
- Weaviate 
- PgVector (PostGres with Vector Extention)
- Pinecone

Croma was the first choice that we experimented with. However, we ran into issues with basic setup. Managaing python pip failures became frustrating and we abondoned this db before we even had it up and running locally. We assumed that deploying a Docker Container with Croma was going to also be a pain. 

Cosmos is the most expesnive and hardest to use. We might end up there eventually, but for the purpose of this POC, we decided to defer. 

Pinecone is the next option on our list. We like it because it is a fully managed DB as a Service. We also noticed that there was a STEEP reduction in pricingin late 2023. Its a FRACTION of what it used to cost. If their online calculator is accurate, this might cost us less than the monthly spend for the Digital Ocean PostGres DB. 

https://www.pinecone.io/pricing/

# Indexes for PineCone DB
Ultimatly, we'll want to explore a map that has embedded each text field and then see what clusters or relationships might be demonstrated. I can probably start in this priority order:

### Embeddings for Job Postings
- Text for full_posting_description
- Text for job_description
- Company Names
- posting_url TEXT NOT NULL,
- job_title 
- is_ai 
- job_salary 
- job_posting_company_information
- job_posting_date 

### Embeddings for Companies
As we add more data about companies, its going to become useful to explore the information we can gather by embedding the text fields for companies. 

- Company Names
- Company About Us
- Company Summary from parsing their top level URLs



### Combinations to explore:
We should think about the ability to ADD two vectors together so that we can say things like, (job_description AND is_ai). We bet this will produce some amount of clusters in the data so that the AI jobs are more likely grouped together. 


# Embedding Models to explore

- OpenAI ADA
- BERT



# Dimensionaility Reduction Tecniques

- TSNE
- UMAP

