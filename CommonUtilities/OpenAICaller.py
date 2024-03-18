import logging
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv('.env')

class OpenAICaller:
    def __init__(self):
        
        logging.info(f"{self.__class__.__name__} class initialized")

    #We can toggle between the two models. 3.5T and 4T
    # gpt-4-turbo-preview
    # gpt-3.5-turbo-16k
        
    def get_completion(self, prompt, model="gpt-3.5-turbo-16k"):
        # gets API Key from environment variable OPENAI_API_KEY
        client = OpenAI()

        completion = client.chat.completions.create(
            model=model,
            messages=prompt,
            max_tokens=6000,
            temperature=0.6,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0

        )
        return completion.choices[0].message.content
    
    def get_embedding(self, text):

        client = OpenAI()
        response = client.embeddings.create(
            input="Your text string goes here",
            model="text-embedding-ada-002"
            )
        return response
    