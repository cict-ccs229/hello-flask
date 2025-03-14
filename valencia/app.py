from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv, dotenv_values
from google import genai
import json
from pydantic import BaseModel

class Diagnosis(BaseModel):
    key_id: str
    primary_name: str
    consumer_name: str
    word_synonyms: str
    synonyms: list[str]
    info_link_data: list[list[str]]

# Load environment variables
load_dotenv()
config = dotenv_values(".env")

# Initialize the Gemini client
client = genai.Client(api_key=config['GEMINI_API_KEY'])

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Load data from diseases.json file
with open('diseases.json') as f:
    diseases = json.load(f)

@app.route("/")
def home():
    """Home route that renders a modernized minimalist template."""
    return render_template("index.html")

@app.route('/diseases', methods=['GET'])
def get_diseases():
    """Retrieve the list of all diseases from local JSON."""
    return jsonify(diseases)

@app.route('/chat', methods=['GET'])
def get_chat():
    """Generate a basic diagnostic example."""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            "You are a medical diagnostic expert.",
            "Analyze the following symptoms: black skin spots, swelling, fever, vomiting, and headache.",
            "The patient has been experiencing the symptoms for a week.",
            "Provide a diagnosis along with confidence levels for possible diseases."
        ]
    )
    return response.text

@app.route('/diagnosis', methods=['GET'])
def get_diagnosis():
    """Provide diagnosis based on symptoms provided by the user."""
    symptoms = request.args.get('symptoms', '').lower()
    if not symptoms:
        return jsonify({"error": "Symptoms parameter is required."}), 400

    # Generate diagnosis with confidence levels
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            f"This is the existing data in JSON format: {json.dumps(diseases)}",
            f"Match the closest disease with the following symptoms: {symptoms}",
            "Provide the most likely disease with a confidence percentage.",
            "List the next three closest diseases with their confidence levels.",
            "Include the info_link_data for all matches in the response."
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": list[Diagnosis]
        }
    )
    try:
        # Parse and format response
        diagnosis = json.loads(response.text)
        return jsonify(diagnosis)
    except Exception as e:
        return jsonify({"error": "Failed to parse response from Gemini API.", "details": str(e)}), 500

@app.route('/search', methods=['GET'])
def search():
    """Search diseases or procedures by primary name, synonyms, or keywords."""
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify({"error": "Query parameter is required."}), 400

    results = [
        item for item in diseases
        if query in item['primary_name'].lower() or
           any(query in synonym.lower() for synonym in item.get('synonyms', [])) or
           query in item.get('word_synonyms', '').lower()
    ]
    return jsonify(results if results else {"message": "No results found."})

if __name__ == '__main__':
    app.run(debug=True)
