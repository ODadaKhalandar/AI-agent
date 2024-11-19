import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv("SERPAPI_API_KEY")
query = "OpenAI contact email"  # Example query

# Make the request to SerpAPI
response = requests.get("https://serpapi.com/search", params={"q": query, "api_key": api_key})

# Print the response to check if it works
print(response.json())