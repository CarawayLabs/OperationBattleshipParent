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


class JobPostingDao:
    def __init__(self):
        logging.info(f"{self.__class__.__name__} class initialized")

    def execute_db_command(sql_statement, data):

        return
    
    
    def getAllDataScienceOrProductCategorizedJobs(self):
        """
        This function calls the Job Posting Table to find all the records that have a job_category of Data Science or Product
        Returns the list as a Pandas Dataframe
        
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
            
            # Execute the SQL query. We know that the is_ai column will be null when the data is raw. 
            cur.execute("SELECT * FROM job_postings WHERE job_category IN ('Product_Management', 'Data_Science')")

            # Fetch all the rows
            rows = cur.fetchall()

            # Convert the results into a pandas DataFrame
            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            # Close the cursor and connection
            cur.close()
            conn.close()

            # Return the DataFrame
            return df

        except Exception as e:
            print("Database connection error:", e)
            logging.info(f"Database error in JobPosting.getUnprocessedAiClassificationJobs. ")  
            conn.close()
        return


        return 
    
    def getAllProductManagerJobs(self):
        """
        This fuction calls the Job Posting Table to find all the records that contain either AI or Product Manager in the title.  
    
        """
        # Establish a connection to the database
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
            
            # Execute the SQL query. We know that the is_ai column will be null when the data is raw. 
            cur.execute("SELECT * FROM job_postings WHERE (job_title ILIKE '%AI%' OR job_title ILIKE '%Product Manager%')")

            # Fetch all the rows
            rows = cur.fetchall()

            # Convert the results into a pandas DataFrame
            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            # Close the cursor and connection
            cur.close()
            conn.close()

            # Return the DataFrame
            return df

        except Exception as e:
            print("Database connection error:", e)
            logging.info(f"Database error in JobPosting.getUnprocessedAiClassificationJobs. ")  
            conn.close()
        return
    
    """
    This method will update the given LinkedIn Job Posting with today's date for most recent updated date. 
    """
    def updateLinkedInJobRecordUpdatedDate(self, jobUrl):
         # Establish a connection to the database
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
            
            # Code to construct a SQL query from the job_posting dataframe
            # Assuming job_posting is a single record from your DataFrame
            sql_update_query = """
            UPDATE job_postings
            SET job_last_collected_date = %s
            WHERE posting_url = %s;
            """
            # Prepare data tuple to be updated
            todaysDate = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S'), 
            data = (todaysDate, jobUrl)
            
            # Execute the SQL query
            cur.execute(sql_update_query, data)
            
            # Commit the transaction
            conn.commit()

            # Close the cursor and connection
            cur.close()
            conn.close()

            # Return success or some form of acknowledgment
            return "Update successful!"

        except Exception as e:
            print("Database connection error:", e)
            conn.close()
            return None
    
    def update_job_posting(self, job_posting):
 
        # Dynamically build the SET part of the SQL statement
        set_sql = ', '.join([f"{col} = %s" for col in job_posting.index if col != 'job_posting_id'])

        # Create the SQL statement
        sql_update_query = f"""
        UPDATE job_postings
        SET {set_sql}
        WHERE job_posting_id = %s;
        """

        # Prepare data tuple to be updated (exclude job_posting_id and append it at the end for the WHERE clause)
        data = tuple(job_posting[col] for col in job_posting.index if col != 'job_posting_id') + (job_posting['job_posting_id'],)

        # Establish a connection to the database
        try:
            conn = psycopg2.connect(
                host=os.getenv("host"),
                database=os.getenv("database"),
                user=os.getenv("digitalOcean"),  
                password=os.getenv("password"),
                port=os.getenv("port")
            )

            # Use a context manager to handle the cursor's opening and closing
            with conn:
                with conn.cursor() as cur:
                    # Execute the SQL query
                    cur.execute(sql_update_query, data)

            # Logging and return message
            logging.info("Update successful for job_posting_id: %s", job_posting['job_posting_id'])
            return "Update successful!"

        except Exception as e:
             # Log the error along with the SQL query and data
            logging.error("Database connection error: %s. SQL: %s, Data: %s", e, sql_update_query, data)
            # Optionally, you might want to format the SQL string to replace placeholders with actual data for clearer logging
            try:
                formatted_sql = cur.mogrify(sql_update_query, data).decode("utf-8")
                logging.error("Formatted SQL sent to DB: %s", formatted_sql)
            except Exception as mogrify_error:
                logging.error("Error formatting SQL: %s", mogrify_error)

        finally:
            # Close the connection if it's open
            if conn is not None:
                conn.close()

    
    def fetchPmJobsRequiringEnrichment(sef):
        """
        This fuction calls the Job Posting Table to find all the PM records that need further enrichment. 
        This process adds salary details, AI Details and basic job description info. 
        """
        # Establish a connection to the database
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
            
            # Execute the SQL query. We know that the is_ai column will be null when the data is raw. 
            cur.execute("SELECT * FROM job_postings WHERE (job_title ILIKE '%AI%' OR job_title ILIKE '%Product Manager%') AND is_ai IS NULL order by job_posting_date desc;")

            # Fetch all the rows
            rows = cur.fetchall()

            # Convert the results into a pandas DataFrame
            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            # Close the cursor and connection
            cur.close()
            conn.close()

            # Return the DataFrame
            return df

        except Exception as e:
            print("Database connection error:", e)
            logging.info(f"Database error in JobPosting.getUnprocessedAiClassificationJobs. ")  
            conn.close()
            return None


    def fetchJobsRequiringEnrichment(self):
        """
        This fuction calls the Job Posting Table to find all the records that need further enrichment. 
        This process adds salary details, AI Details and basic job description info. 
        """
        # Establish a connection to the database
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
            
            # Execute the SQL query. We know that the is_ai column will be null when the data is raw. 
            cur.execute("SELECT * FROM job_postings WHERE is_ai IS NULL")

            # Fetch all the rows
            rows = cur.fetchall()

            # Convert the results into a pandas DataFrame
            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            # Close the cursor and connection
            cur.close()
            conn.close()

            # Return the DataFrame
            return df

        except Exception as e:
            print("Database connection error:", e)
            logging.info(f"Database error in JobPosting.getUnprocessedAiClassificationJobs. ")  
            conn.close()
            return None
    
    def checkIfJobExists(self, cleanedLinkedInJobURL):
        try:
            # Establish a connection to the database
            conn = psycopg2.connect(
                host=os.getenv("host"),
                database=os.getenv("database"),
                user=os.getenv("digitalOcean"),  # Assuming this is the correct env variable name
                password=os.getenv("password"),
                port=os.getenv("port")
            )
            # Create a new cursor
            cur = conn.cursor()

            # Prepare the SQL command
            sql_command = "SELECT * FROM job_postings WHERE posting_url = %s"
            
            

            # Execute the SQL command
            cur.execute(sql_command, (cleanedLinkedInJobURL, ))
            
            # Fetch all the rows
            rows = cur.fetchall()

            # Close the cursor and connection
            cur.close()
            conn.close()

            # Check the number of rows returned and return True or False
            return len(rows) > 0

        except Exception as e:
            # Log or print the error for debugging
            print("Database connection error:", e)
            logging.info(f"Database error in JobPosting.checkIfJobExists for Job at: {cleanedLinkedInJobURL} ")  
            
            mogrified_query = cur.mogrify(sql_command, (cleanedLinkedInJobURL, )).decode('utf-8')
            logging.info(f"Executing SQL command: {mogrified_query}")
            # Close the connection in case of error
            if 'conn' in locals():
                conn.close()
            return False  # You might want to return False or re-raise the exception depending on your use case
        

    def insertNewJobRecord(self, jobpostingDataFrame):

        conn = None
        try:
            # Establish a connection to the database
            conn = psycopg2.connect(
                host=os.getenv("host"),
                database=os.getenv("database"),
                user=os.getenv("digitalOcean"),
                password=os.getenv("password"),
                port=os.getenv("port")
            )
            # Create a new cursor
            cur = conn.cursor()

            # SQL statement for inserting data
            insert_sql = """INSERT INTO job_postings (
                job_posting_id, company_id, posting_url, posting_source, posting_source_id, job_title,
                 full_posting_description, job_description, is_ai, job_salary, job_posting_company_information, 
                 job_posting_date, job_insertion_date, job_last_collected_date, job_active, city, state
            ) Values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Assuming there's only one row in the DataFrame, access the first row directly
            # Convert the UUID to a string if the column is expected to be a UUID
            row = jobpostingDataFrame.iloc[0].apply(lambda x: str(x) if isinstance(x, uuid.UUID) else x)
            
            # Log the SQL statement and data. We can uncomment the log file line below when we want more verbose logging. 
            #logging.info(f"Executing SQL: {insert_sql} with data: {tuple(row)}")

            cur.execute(insert_sql, tuple(row))
            conn.commit()

            # Close the cursor and connection
            cur.close()
            conn.close()
            return 1

        except Exception as e:
            # Log or print the error for debugging

            logging.info(f"Database error: {e}")
            logging.info(f"Database error in JobPosting.insertNewJobRecord for Job at: {jobpostingDataFrame['posting_url']} ")
            logging.info(f"Executing SQL: {insert_sql} with data: {tuple(row)}")  
            # Close the connection in case of error
            if conn:
                conn.close() 
            
            return -1
        
    def getAllJobs(self):
        """
        This fuction calls the Job Posting Table to find all the records and returns them to the user as a pandas pd 
        """
        # Establish a connection to the database
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
            
            # Execute the SQL query. We know that the is_ai column will be null when the data is raw. 
            cur.execute("SELECT * FROM job_postings")

            # Fetch all the rows
            rows = cur.fetchall()

            # Convert the results into a pandas DataFrame
            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            # Close the cursor and connection
            cur.close()
            conn.close()

            # Return the DataFrame
            return df

        except Exception as e:
            print("Database connection error:", e)
            logging.info(f"Database error in JobPosting.getUnprocessedAiClassificationJobs. ")  
            conn.close()
            return None
        
    def getCurrentJobsIdsAsDataFrame(self):
        """
        This fuction calls the Job Posting Table to find all the records and returns them to the user as a pandas pd 
        """
        # Establish a connection to the database
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
            
            # Execute the SQL query. We know that the is_ai column will be null when the data is raw. 
            cur.execute("SELECT posting_url FROM job_postings")

            # Fetch all the rows
            rows = cur.fetchall()

            # Convert the results into a pandas DataFrame
            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            # Close the cursor and connection
            cur.close()
            conn.close()

            # Return the DataFrame
            return df

        except Exception as e:
            print("Database connection error:", e)
            logging.info(f"Database error in JobPosting.getCurrentJobsIdsAsDataFrame. ")  
            conn.close()
            return None
    
    def getProductManagerJobs(self):

        return
    
    def getUncategorizedJobs(self):
        
        """
        This fuction calls the Job Posting Table to find all the PM records that need further enrichment. 
        This process adds salary details, AI Details and basic job description info. 
        """
        # Establish a connection to the database
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
            
            # Execute the SQL query. We know that the is_ai column will be null when the data is raw. 
            cur.execute("SELECT * FROM job_postings WHERE job_category is null;")

            # Fetch all the rows
            rows = cur.fetchall()

            # Convert the results into a pandas DataFrame
            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            # Close the cursor and connection
            cur.close()
            conn.close()

            # Return the DataFrame
            return df

        except Exception as e:
            print("Database connection error:", e)
            logging.info(f"Database error in JobPosting.getUnprocessedAiClassificationJobs. ")  
            conn.close()
            return None


        return
    
    def getjobsFromListOfJobsIds(self, dataframeOfJobIds):
        """
        Purpose: When given a list of Job_Ids, this function will call the job_postings table and return the list of jobs that match the given IDs. 

        Args:
            dataframeOfJobIds: Pandas Dataframe where one column contains 'id' and this corresponds to job_posting_id in the Postgres DB

        Return Value:
            Pandas Dataframe of each job record, company name and aother associated metadata.  
        """
        job_ids = dataframeOfJobIds['job_posting_id'].tolist()

        # Convert list of job_ids to tuple for SQL query
        job_ids_tuple = tuple(job_ids)

        # SQL query
        sql_query = f"""
        SELECT
            c.company_name,
            jp.job_title,
            jp.posting_url,
            jp.full_posting_description,
            jp.job_description,
            jp.is_ai,
            jp.is_genai,
            jp.salary_low,
            jp.salary_midpoint,
            jp.salary_high,
            jp.job_salary,
            jp.job_category,
            jp.job_posting_date,
            jp.job_posting_id AS job_posting_id,
            jp.company_id,
            jp.posting_source,
            jp.posting_source_id,
            jp.job_posting_company_information,
            jp.job_insertion_date,
            jp.job_last_collected_date,
            jp.job_active,
            jp.city,
            jp.state,
            jp.job_skills,
            jp.is_ai_justification,
            jp.work_location_type
        FROM
            job_postings jp
        JOIN
            companies c ON jp.company_id = c.company_id
        WHERE
            jp.job_posting_id IN %s;
        """
        # Establish a connection to the database
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

            # Execute the SQL query with parameterized input for safety
            cur.execute(sql_query, (job_ids_tuple,))

            # Fetch all the rows
            rows = cur.fetchall()

            # Convert the results into a pandas DataFrame
            if rows:
                df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
            else:
                df = pd.DataFrame()

            # Close the cursor and connection
            cur.close()
            conn.close()

            return df

        except Exception as e:
            print("Database connection error:", e)
            conn.close()
            return pd.DataFrame()
