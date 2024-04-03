"""
This Python script defines a CompanyDao class that provides an interface for interacting with a PostgreSQL database that stores company data. The class includes methods for executing generic SQL commands, retrieving all companies, getting a company’s UUID by its LinkedIn URL, checking if a company exists in the database by its LinkedIn URL, and inserting new company data into the database. The script uses environment variables for secure database connection and includes logging for tracking operations and errors. The CompanyDao class is initialized with no arguments, and each method within the class serves a specific purpose related to the manipulation and retrieval of company data from the database. The script is designed to be used as a data access object in a larger application where company data needs to be stored and retrieved.

"""

import os
import uuid
from dotenv import load_dotenv
import pandas as pd
import psycopg2
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CompanyDao:
    def __init__(self):
        logging.info(f"{self.__class__.__name__} class initialized")

    def genericSQL(sqlString):

        return


    """
    TODO: This function will need actual logic
    
    """
    def get_all_companies():

        companyDataFrame = []

        return companyDataFrame
    
    """
    When given a URL for the Company's LinkedIn Page, we want to get the UUID from the Companies Table. 
    """
    def getCompanyUuidByLinkedInUrl(self, companyLinkedinUrl):
        try:
            # Establish a connection to the database
            conn = psycopg2.connect(
                host=os.getenv("host"),
                database=os.getenv("database"),
                user=os.getenv("digitalOcean"),  # Ensure correct environment variable name
                password=os.getenv("password"),
                port=os.getenv("port")
            )
            # Create a new cursor
            cur = conn.cursor()
            
            # Execute the SQL query with parameterized input
            cur.execute("SELECT company_id FROM Companies WHERE linkedin_url = %s", (companyLinkedinUrl,))
            
            # Fetch all the rows
            rows = cur.fetchall()
            
            # Close the cursor and connection
            cur.close()
            conn.close()

            # Check the number of rows returned and return the company_id
            if rows:
                return rows[0][0]  # Assuming there's always one unique ID per LinkedIn URL
            else:
                logging.info(f"Error in getting Company ID. We always expect an ID in this function. Failed for: {companyLinkedinUrl} ")
                return None  # Or appropriate error handling/message

        except Exception as e:
            # Log or print the error for debugging
            print("Database connection error:", e)
            logging.info(f"Database error in CompanyDao.getCompanyUuidByLinkedInUrl for Company at: {companyLinkedinUrl} ")
            # Close the connection in case of error
            if 'conn' in locals():
                conn.close()
            return None
    
    """
    This function will check the company table and determine if this table contains any records with this company URL. 

    """
    def doesCompanyExist(self, linkedInCompanyUrl):
        
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
            
            # Execute the SQL query with parameterized input
            cur.execute("SELECT * FROM companies WHERE linkedin_url = %s", (linkedInCompanyUrl, ))    
            
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
            logging.info(f"Database error in CompanyDao.doesCompanyExist for Company at: {linkedInCompanyUrl} ")           
            # Close the connection in case of error
            if 'conn' in locals():
                conn.close()
            return False  # You might want to return False or re-raise the exception depending on your use case
    

    def insertCompany(self, companyDataFrame):
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
            insert_sql = """
            INSERT INTO Companies (
                company_id, company_name, company_website, linkedin_url, industry, 
                num_employees, ownership_type, about_webpage, careers_page, 
                home_page_summary, about_page_summary, linkedin_company_summary, 
                has_datascience, has_product_operations
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Assuming there's only one row in the DataFrame, access the first row directly
            row = companyDataFrame.iloc[0].apply(lambda x: str(x) if isinstance(x, uuid.UUID) else x)
            cur.execute(insert_sql, tuple(row))

            # Commit the changes
            conn.commit()

            # Close the cursor and connection
            cur.close()
            conn.close()

        except Exception as e:
            # Log or print the error for debugging
            print("Database connection error:", e)
            logging.info(f"Database error in CompanyDao.insertCompany for Company at: {companyDataFrame["company_name"]} ")  
            # Close the connection in case of error
            if conn:
                conn.close()

    def getCompanyNameByCompanyId(self, company_id):

        try:
            # Establish a connection to the database
            conn = psycopg2.connect(
                host=os.getenv("host"),
                database=os.getenv("database"),
                user=os.getenv("digitalOcean"),  # Ensure correct environment variable name
                password=os.getenv("password"),
                port=os.getenv("port")
            )
            # Create a new cursor
            cur = conn.cursor()
            
            # Execute the SQL query with parameterized input
            cur.execute("SELECT company_name FROM Companies WHERE company_id = %s", (company_id,))
            
            # Fetch all the rows
            rows = cur.fetchall()
            
            # Close the cursor and connection
            cur.close()
            conn.close()

            # Check the number of rows returned and return the company_id
            if rows:
                return rows[0][0]  # Assuming there's always one unique company name per company ID
            else:
                logging.info(f"Error in getting Company Name. We always expect an name in this function. Failed for company id: {company_id} ")
                return None  # Or appropriate error handling/message

        except Exception as e:
            # Log or print the error for debugging
            print("Database connection error:", e)
            logging.info(f"Database error in CompanyDao.getCompanyNameByCompanyId for Company at: {company_id} ")
            # Close the connection in case of error
            if 'conn' in locals():
                conn.close()
            return None