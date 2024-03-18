"""
This script defines the GeographyHelper class, which provides functionality for parsing and extracting city and state information from a given string. The class uses regular expressions to match patterns and returns the results as a pandas DataFrame. It is designed to help standardize geographical data for further processing or analysis.

"""
import logging
import re
import pandas as pd


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GeographyHelper :
    def __init__(self):
        logging.info(f"{self.__class__.__name__} class initialized")


    def getCityState(self, cityStateString):

            # Regular expression to match the patterns "City, State" or "State, Country"
        pattern = re.compile(r"([A-Za-z\s\-]+)(?:, )?([A-Z]{2})?")

        # Apply the pattern to the string
        match = pattern.match(cityStateString)

        # Initialize city and state as None
        city, state = None, None

        if match:
            # If the first group (city/region) is a known state or 'United States', set it as state
            if match.group(1).strip() in ["United States"] or match.group(1).strip() in us_states:
                state = match.group(1).strip()
            else:
                city = match.group(1).strip()
                state = match.group(2)

        # Return the results as a DataFrame
        return pd.DataFrame({"city": [city], "state": [state]})

us_states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
            "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois",
            "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
            "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
            "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
            "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
            "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
            "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
