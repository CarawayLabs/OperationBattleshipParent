"""
Purpose: We've discovered that the job_posting_date is stored as a string in Pinecone. It needs to be an integer instead. To accomplish this, we will open a file that contains all of the IDs for each of the three namespaces and then convert the date as a string into an integer. Then, we upsert the values back into the DB. 

"""
import logging
import os
from dotenv import load_dotenv
from datetime import datetime

from pinecone import Pinecone, ServerlessSpec

logging.basicConfig(level=logging.INFO)

load_dotenv('.env')

# Convert date string to integer relative to an epoch
def date_to_integer(date_str, epoch_str='1970-01-01'):
    date = datetime.strptime(date_str, '%Y-%m-%d')
    epoch = datetime.strptime(epoch_str, '%Y-%m-%d')
    delta = date - epoch
    return delta.days

def read_ids_from_file(filename):
    with open(filename, 'r') as file:
        ids = [line.strip() for line in file]
    return ids

def chunk_ids(ids, chunk_size=100):
    for i in range(0, len(ids), chunk_size):
        yield ids[i:i+chunk_size]

def process_batches(filename, namespace):

    index_name = "job-postings"
    pineconeApiKey = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=pineconeApiKey)
    index = pc.Index(index_name)

    ids = read_ids_from_file(filename)
    for batch in chunk_ids(ids):
        vectors = index.fetch(ids=batch, namespace=namespace)
        updates = []
        for id, vector_data in vectors['vectors'].items():
            job_posting_date = vector_data['metadata']['job_posting_date']
            # Ensure job_posting_date is an integer
            if not isinstance(job_posting_date, int):
                # Convert to integer if it's a string; also handles floats correctly
                job_posting_date = date_to_integer(job_posting_date) if isinstance(job_posting_date, str) else int(job_posting_date)
            else:
                # If already an int, ensure it's purely an integer (handle floats if present)
                job_posting_date = int(job_posting_date)

            vector_data['metadata']['job_posting_date'] = job_posting_date
            # Append the possibly updated vector data to updates
            updates.append({
                'id': id,
                'values': vector_data['values'],
                'metadata': vector_data['metadata']
            })
        # Upsert the updated vector data back into Pinecone
        index.upsert(vectors=updates, namespace=namespace)
        logging.info(f"Updated and upserted {len(updates)} vectors.")

# Main function to kick off processing
if __name__ == "__main__":
    """
    filename = "Utilities/full-posting-description.txt"
    namespace = "full-posting-description"
    process_batches(filename, namespace)

    filename = "Utilities/job-title.txt"
    namespace = "job-title"
    process_batches(filename, namespace)
    """
    

    filename = "Utilities/short-job-description.txt"
    namespace = "short-job-description"
    process_batches(filename, namespace)
