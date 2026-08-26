import os 
from dotenv import load_dotenv
from google import genai
from google.genai import types
#load API configuration
load_dotenv()
api_key= os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")
#configure Gemini Client
Client = genai.Client(api_key=api_key,
                      http_options=types.HttpOptions(
                          retry_options= types.HttpRetryOptions(
                              attempts = 4,
                              initial_delay=1.0,
                              max_delay=10.0,
                              http_status_codes =[408,429,500,502,503,504]
                          )
                      ))
#create Gemini chat session
chat =Client.chats.create(model="gemini-3.6-flash")
#send content to Gemini
def send_to_gemini(contents):
    response = chat.send_message(contents)
    return response.text
