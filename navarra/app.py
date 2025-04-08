from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv, dotenv_values
from pydantic import BaseModel
import json
import os
import google.generativeai as genai

class Diagnosis(BaseModel):
    key_id: str
    primary_name: str
    diagnosis: str
    consumer_name: str
    word_synonyms: str
    synonyms: list[str]
    info_link_data : list[list[str]]
    treatments: str

load_dotenv()

key = os.getenv('API_KEY')
if not key:
    raise ValueError("API key not found")

if not key:
    raise ValueError("API key is missing")

try:
    genai.configure(api_key=key)
    print("Google Generative AI configured successfully!")
except Exception as e:
    print(f"Configuration error: {e}")
    raise ValueError("Failed to configure client with the API key")

app = Flask(__name__)

# Load the JSON file
with open('diseases.json', encoding="utf-8") as file:  # Works cross-platform
    data = json.load(file)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diseases')
def diseases():
    return jsonify(data)
@app.route('/search_disease', methods=['POST'])
def search_disease():
    query = request.json.get('query', '').strip().lower()
    
    if not query:
        return jsonify({'error': 'Search keyword is required'}), 400

    # Find all diseases that match the search term
    matches = [disease for disease in data if query in disease["primary_name"].lower()]

    if matches:
        return jsonify(matches)
    else:
        return jsonify({'error': 'No diseases found'}), 404

@app.route('/disease/<key_id>')
def get_disease(key_id):
    disease_info = next((d for d in data if d["key_id"] == key_id), None)

    if disease_info:
        # Ensure word_synonyms is a list
        if "word_synonyms" in disease_info and isinstance(disease_info["word_synonyms"], str):
            disease_info["word_synonyms"] = disease_info["word_synonyms"].split(";")

        return render_template('disease_details.html', disease=disease_info)
    else:
        return "Disease not found", 404
    
@app.route('/chat', methods=['GET'])
def chat():
    return render_template("chat.html")

# Route for generating diagnosis based on disease name
@app.route('/get_diagnosis', methods=['POST'])
def get_diagnosis():
    data = request.get_json()
    disease_name = data.get("disease_name", "").strip()

    if not disease_name:
        return jsonify({"error": "Please enter a disease name."}), 400

    model = genai.GenerativeModel("gemini-1.5-flash-002")
    
    response = model.generate_content(
        contents=[
            f"Diagnose a patient with {disease_name}. Provide symptoms, possible causes, and treatment options."
        ]
    )
    
    return jsonify({"diagnosis": response.text})

@app.route('/diagnosis', methods=['GET'])
def diagnosis():
    symptoms = request.args.get('symptoms', '').strip().lower()
    model = genai.GenerativeModel("gemini-1.5-flash-002")
    response = model.generate_content(
        contents=[
            "This is the existing data in JSON format: " + json.dumps(data),
            "Match the closest disease with following symptoms: " + symptoms,
            "Include the info_link_data in the response.",
            "Return the top three matching items."
        ],
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": list[Diagnosis]
        }
    )

    return json.loads(response.text)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=10000)