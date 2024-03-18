"""
This script defines the JobKeyWordsDao class, which provides functionality for inserting job keywords into a database. The class uses the psycopg2 library to connect to a PostgreSQL database and execute SQL queries. It reads job keywords from a pandas DataFrame and inserts each record into the 'Job_Keywords' table in the database. The script uses environment variables to securely access database credentials. Logging is configured for tracking the execution of the script.
"""
import os
from datetime import datetime
import uuid
import logging
from dotenv import load_dotenv
import pandas as pd
import psycopg2

load_dotenv('.env')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class JobKeyWordsDao :
    def __init__(self):
        logging.info(f"{self.__class__.__name__} class initialized")


    def insertJobKeyWordsForJobPosting(self, jobKeyWordsDataFrame):
        """
        When given a dataframe that has multiple records, this function will insert each record into the DB. 
        """

        conn = psycopg2.connect(
            host=os.getenv("host"),
            database=os.getenv("database"),
            user=os.getenv("digitalOcean"),
            password=os.getenv("password"),
            port=os.getenv("port")
        )
        try:
            # Create a new cursor
            cur = conn.cursor()

            # Prepare the SQL insert statement
            sql_insert_query = "INSERT INTO Job_Keywords (job_posting_id, unique_id, item) VALUES (%s, %s, %s)"

            # Loop through each row in the DataFrame and insert it into the database
            for index, row in jobKeyWordsDataFrame.iterrows():

                # Convert UUID to string before insertion
                job_posting_id_str = str(row['job_posting_id'])
                unique_id_str = str(row['unique_id'])
                data = (job_posting_id_str, unique_id_str, row['item'])
                cur.execute(sql_insert_query, data)
                
            # Commit the transaction

            conn.commit()

            # Close the cursor and connection
            cur.close()
            conn.close()

            # Return success or some form of acknowledgment
            return "Update successful!"

        except Exception as e:
            print("Database connection error:", e)
            # Ensure connection is closed even if error occurs
            conn.close()
            return None
