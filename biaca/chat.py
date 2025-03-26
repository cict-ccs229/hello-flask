from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
import google.generativeai as genai
import json
import os  
from pydantic import BaseModel

# Define the Blueprint
chat_bp = Blueprint('chat', __name__)

# Pydantic model for structured diagnosis data
class Diagnosis(BaseModel):
    key_id: str
    primary_name: str
    consumer_name: str
    word_synonyms: str
    synonyms: list[str]
    info_link_data: list[list[str]]

# Load environment variables from .env file if it exists
load_dotenv()

# Get API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Ensure API key exists
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY environment variable")

# Configure the Generative AI client
genai.configure(api_key=GEMINI_API_KEY)

# Load disease data
try:
    with open('diseases.json') as f:
        diseases = json.load(f)
except FileNotFoundError:
    diseases = []

@chat_bp.route("/diseases", methods=['GET'])
def get_diseases():
    """Returns the list of diseases from the JSON file."""
    return jsonify(diseases)

@chat_bp.route("/message", methods=['POST'])
def chat_message():
    """Handles user chat messages and allows Gemini to look up diseases.json dynamically."""
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "Message cannot be empty"}), 400

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content([
        f"You are a medical assistant. Use the following disease data to answer user questions:",
        json.dumps(diseases),  
        f"User query: {user_input}. If relevant, reference the diseases.json data for an accurate response."
    ])

    reply = response.text if hasattr(response, 'text') else response.candidates[0].content
    return jsonify({"reply": reply})


@chat_bp.route('/diagnosis', methods=['GET'])
def get_diagnosis():
    """Finds the closest matching diseases based on given symptoms using AI."""
    symptoms = request.args.get('symptoms', '').strip().lower()

    if not symptoms:
        return jsonify({"error": "Symptoms parameter is required"}), 400

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content([
        f"This is the existing data in JSON format: {json.dumps(diseases)}",
        f"Match the closest disease with the following symptoms: {symptoms}",
        "Include the info_link_data in the response.",
        "Return the top three matching items in valid JSON format."
    ])

    try:
        diagnosis_data = json.loads(response.text)
        return jsonify(diagnosis_data)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON response from AI"}), 500