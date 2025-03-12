from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv, dotenv_values
from google import genai
from pydantic import BaseModel
import json
import os
import requests

app = Flask(__name__)

# Load diseases data
with open(os.path.join(os.path.dirname(__file__), 'diseases.json')) as f:
    diseases = json.load(f)

class Diagnosis(BaseModel):
    key_id: str
    primary_name: str
    consumer_name: str
    word_synonyms: str
    synonyms: list[str]
    info_link_data: list[list[str]]

load_dotenv()
config = dotenv_values(".env")
client = genai.Client(api_key=config['GEMINI_API_KEY'])

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/diseases', methods=['GET'])
def get_diseases():
    return jsonify(diseases)

@app.route('/match', methods=['POST'])
def match_diseases():
    symptoms = request.form.get('symptoms', '').lower().split(',')
    matched_diseases = []

    for disease in diseases:
        disease_symptoms = disease.get('synonyms', [])
        if any(symptom.strip() in disease_symptoms for symptom in symptoms):
            matched_diseases.append(disease['primary_name'])

    return jsonify(matched_diseases)

@app.route('/lookup', methods=['POST'])
def lookup_disease():
    query = request.form.get('query', '').lower()
    print(f"Query: {query}")
    results = []

    for disease in diseases:
        if query in disease.get('primary_name', '').lower() or query in disease.get('icd10cm_codes', '').lower():
            results.append({
                'primary_name': disease.get('primary_name'),
                'synonyms': disease.get('synonyms', []),
                'info_links': disease.get('info_link_data', []),
                'icd10cm_codes': disease.get('icd10cm_codes', ''),
                'is_procedure': disease.get('is_procedure', False)
            })

    return jsonify(results)

@app.route('/chat', methods=['GET', 'POST'])
def get_chat():
    diagnosis = None
    if request.method == 'POST':
        symptoms = request.form.get('symptoms', '').lower()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                "You are a disease diagnosing staff",
                f"Create a basic diagnosis for a patient with the following symptoms: {symptoms}.",
                "The patient has been experiencing the symptoms for a week already",
                "Provide an accurate diagnosis"
            ]
        )
        diagnosis = response.text
    return render_template('chat.html', diagnosis=diagnosis)

@app.route('/diagnosis', methods=['GET'])
def get_diagnosis():
    symptoms = request.args.get('symptoms', '').lower()
    response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
    "This is the existing data in JSON format: " + json.dumps(diseases),
    "Match the closest disease with following symptoms: " + symptoms,
    "Include the info_link_data in the response.",
    "Return the top three matching items."
    ],

    config={
    "response_mime_type": "application/json",
    "response_schema": list[Diagnosis]
    }
    )
    return json.loads(response.text)


if __name__ == '__main__':
    app.run(debug=True)