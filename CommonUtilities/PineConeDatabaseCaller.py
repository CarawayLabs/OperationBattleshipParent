import logging
import os
import datetime
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv('.env')


class PineConeDatabaseCaller:

    def __init__(self, api_key):
        self.pc = Pinecone(api_key=api_key)  # Initialize Pinecone client with your API key
        logging.info(f"{self.__class__.__name__} class initialized")

        return
    
    def createIndexIfDoesntExist(self, indexName):
        """
        Checks to see if this index exists in Pinecone. If it does, then just return.
        If the index does not yet exist, create it. 
        """
        if indexName not in self.pc.list_indexes().names():
            self.pc.create_index(name=indexName, 
                                 dimension=768,
                                 metric='cosine',
                                 spec=ServerlessSpec(
                                    cloud="aws",
                                    region="us-west-2"
                                    ) 
                                 )
            logging.info(f"Index {indexName} created.")
        else:
            logging.info(f"Index {indexName} already exists.")

        return

    
    # ...
    def upsertEmbeddings(self, indexName, namespace, embeddingsDictionary):
        index = self.pc.Index(indexName)
        vectors = []
        for id, data in embeddingsDictionary.items():
            logging.info(f"Datatype of the id variable is: {type(id)}")
            logging.info(f"Datatype of the data[embedding] variable is: {type(data['embedding'])}")
            logging.info(f"Datatype of the metadata variable is: {type(data['metadata'])}")
            
            # Ensure embedding is a flat list of floats
            embedding = data['embedding']
            if isinstance(embedding[0], list):  # Checks if the first element is a list, indicating a nested structure
                logging.info(f"Datatype of the first element in the embedding: {type(embedding[0])}")
                embedding = embedding[0]  # Assumes the embedding is the first element of the list
            
            vectors.append({
                'id': id,
                'values': embedding,
                'metadata': data['metadata']
            })
        upsert_response = index.upsert(vectors, namespace=namespace)
        return upsert_response
        
    def query(self, embeddedResume, numberOfNeighbors, indexName, namespace, numberOfDays=45):
        # Calculate the date to filter job postings
        job_posting_date_cutoff = self.getIntegerValueForDayFilter(numberOfDays)

        index = self.pc.Index(indexName)

        # Applying the job_posting_date filter
        result = index.query(
            namespace=namespace,
            vector=embeddedResume,
            filter={"job_posting_date": {"$gte": job_posting_date_cutoff}},  # Adjust this filter as per your requirements
            top_k=numberOfNeighbors,
            include_metadata=True
        )

        return result

    def getIntegerValueForDayFilter(self, numberOfDays):
        """
        Calculate the number of days since the Unix epoch for the date numberOfDays ago.
        """
        today = datetime.date.today()
        cutoff_date = today - datetime.timedelta(days=numberOfDays)
        epoch_start = datetime.date(1970, 1, 1)
        days_since_epoch = (cutoff_date - epoch_start).days
        logging.info(f"Computed days since epoch for cutoff: {days_since_epoch}")
        return days_since_epoch