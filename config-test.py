from dotenv import load_dotenv
import os

# Specify the relative path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), 'napud', '.env')

# Load the environment variables from the .env file
load_dotenv(dotenv_path=dotenv_path)

# Access the GEMINI_API_KEY environment variable
gemini_api_key = os.getenv('GEMINI_API_KEY')

# Check if the GEMINI_API_KEY is present
if not gemini_api_key:
    raise KeyError("GEMINI_API_KEY not found in environment variables")

print("GEMINI_API_KEY found: ", gemini_api_key)
