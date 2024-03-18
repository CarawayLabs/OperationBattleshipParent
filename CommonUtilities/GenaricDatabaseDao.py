"""
This script is intended to be the only class that actually calls the PostGres DB. All other DAO Classes will reference this Class. 

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

class GenaricDatabaseDao:
    def __init__(self):
        logging.info(f"{self.__class__.__name__} class initialized")

    def execute_select_command(sql_statement):

        return
    
    def execute_update_command(sql_statement, data):

        return
    
    def execute_insert_command(sql_statement, data):

        return