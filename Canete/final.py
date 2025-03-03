from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv, dotenv_values
import json
import re
import google.generativeai as genai
from pydantic import BaseModel
from functools import lru_cache

class Diagnosis(BaseModel):
    key_id: str
    primary_name: str
    consumer_name: str
    word_synonyms: str
    synonyms: list[str]
    info_link_data: list[list[str]]

# Load API key
load_dotenv()
config = dotenv_values(".env")

# Configure generative AI
genai.configure(api_key=config['GEMINI_API_KEY'])

# Initialize Flask app
app = Flask(__name__)

# Load diseases data from JSON file
with open('diseases.json') as f:
    diseases = json.load(f)

# Initialize the generative model
model = genai.GenerativeModel('gemini-1.5-flash-latest')  # Use a faster model

def clean_symptoms(symptoms):
    # Remove extra spaces, special characters, etc.
    symptoms = re.sub(r'[^a-zA-Z0-9\s]', '', symptoms)
    symptoms = ' '.join(symptoms.split())  # Remove extra spaces
    return symptoms.lower()

@lru_cache(maxsize=100)  # Cache up to 100 responses
def get_cached_diagnosis(symptoms):
    prompt = (
        f"Here is a list of diseases and their details in JSON format: {json.dumps(diseases)}\n"
        f"Based on the following symptoms: {symptoms}\n"
        "Identify the top 3 most likely diseases and provide the following details for each:\n"
        "- primary_name: The name of the disease\n"
        "- description: A brief overview of the disease\n"
        "- causes: Common causes of the disease\n"
        "- effects: How the disease affects a person\n"
        "- remedies: Up to three effective treatments or home remedies\n"
        "- info_link_data: A list containing a URL and the title for further reading\n"
        "Return the response in valid JSON format without any additional text or markdown formatting."
    )
    response = model.generate_content(prompt)
    return response.text

def parse_response(raw_response):
    try:
        # Remove markdown code block formatting (```json ... ```)
        cleaned_response = re.sub(r"```json\s*([\s\S]*?)\s*```", r"\1", raw_response).strip()
        return json.loads(cleaned_response)
    except json.JSONDecodeError:
        return None

@app.route("/")
def home():
    return render_template("index2.html")

@app.route('/diseases', methods=['GET'])
def get_diseases():
    return jsonify(diseases)

@app.route('/diagnosis', methods=['GET'])
def get_diagnosis():
    symptoms = clean_symptoms(request.args.get('symptoms', ''))

    try:
        raw_response = get_cached_diagnosis(symptoms)
        diagnosis_data = parse_response(raw_response)

        if not diagnosis_data:
            return jsonify({"error": "Invalid response from AI", "raw_response": raw_response}), 500

        return jsonify(diagnosis_data)
    except Exception as e:
        return jsonify({"error": f"Failed to generate response: {str(e)}"}), 500

@app.route('/symptom-suggestions', methods=['GET'])
def get_symptom_suggestions():
    query = clean_symptoms(request.args.get('query', ''))

    try:
        prompt = (
            f"Suggest possible symptoms based on the following input: {query}\n"
            "Return a JSON array of symptom names without any additional text or markdown formatting."
        )
        response = model.generate_content(prompt)
        raw_response = response.text

        suggestions = parse_response(raw_response)
        if not suggestions:
            return jsonify({"error": "Invalid response from AI", "raw_response": raw_response}), 500

        return jsonify(suggestions)
    except Exception as e:
        return jsonify({"error": f"Failed to generate response: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)