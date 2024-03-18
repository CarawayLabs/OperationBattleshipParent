import logging
import os
from dotenv import load_dotenv
import nomic.embed as embed
import nomic 


load_dotenv('.env')

class NomicAICaller:
    def __init__(self):
        
        logging.info(f"{self.__class__.__name__} class initialized")



    def embedDocument(self, document):
        nomicApiKey = os.getenv("NOMIC_API_KEY")
        nomic.login(nomicApiKey)

        embeddedText = embed.text(
            texts=[document],
            model='nomic-embed-text-v1.5',
            task_type='search_document'
            )['embeddings']
        return embeddedText
    




