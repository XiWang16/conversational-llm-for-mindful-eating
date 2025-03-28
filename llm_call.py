from dotenv import load_dotenv
import os
import requests

# Load environment variables from config.env
load_dotenv("config.env")

# Retrieve Hugging Face API key from environment variables
HF_KEY = os.getenv("HF_TOKEN")

# Set API URL for Mistral Instruct model
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

# Set API headers
headers = {"Authorization": f"Bearer {HF_KEY}"}

# Define input data and parameters
question = "Ca va?"
data = {
    "inputs": f"{question}",
    "parameters": {
        "max_length": 200,  # Maximum length of the generated text
        "temperature": 0.7,  # Controls randomness (0.1 to 1.0)
        "top_p": 0.9        # Probability-based sampling (0.1 to 1.0)
    }
}

# Make API request
response = requests.post(API_URL, headers=headers, json=data)

# Process and print the API response
if response.status_code == 200:
    print(response.json()[0]["generated_text"])
else:
    print(f"Error: {response.status_code}, {response.text}")
