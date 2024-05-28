
import pandas as pd
import logging
import sys
import os
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

from operation_battleship_common_utilities.NomicAICaller import NomicAICaller
from operation_battleship_common_utilities.PineConeDatabaseCaller import PineConeDatabaseCaller


load_dotenv()

log_file_path = os.path.join(Path(__file__).parent.absolute(), 'logfile.log')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s',
                    filename=log_file_path,
                    filemode='w')


def main(args):


    return 


if __name__ == "__main__":
    
    args = {"name": sys.argv[1]} if len(sys.argv) > 1 else {}
    main(args)