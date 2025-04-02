from flask import Flask, render_template, request, jsonify
import json
import os
from dotenv import load_dotenv, dotenv_values
from google import genai
from pydantic import BaseModel

class Diagnosis(BaseModel):
    key_id: str
    primary_name: str
    consumer_name: str
    word_synonyms: str
    synonyms: list[str]
    info_link_data: list[list[str]]

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables or .env file.")

client = genai.Client(api_key=gemini_api_key)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
json_path = os.path.join(BASE_DIR, "hallares", "diseases.json")

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "hallares", "frontend"))

with open(json_path, encoding="utf-8") as f:
    app.diseases_data = json.load(f)

def generate_diagnosis(symptoms):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            "This is the existing data in JSON format: " + json.dumps(app.diseases_data),
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

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        symptom = request.form.get("symptom").lower()
        matches = generate_diagnosis(symptom)
        return render_template("results.html", matches=matches, symptom=symptom)
    return render_template("index.html")

@app.route("/disease/<disease_id>")
def disease_details(disease_id):
    disease = next((d for d in app.diseases_data if d["key_id"] == disease_id), None)
    if disease:
        # Generate AI suggestion for the specific disease
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                f"Provide a simple treatment or solution for the disease: {disease['primary_name']}.",
                "Keep it clear and concise for a general audience."
            ]
        )
        ai_suggestion = response.text
        return render_template("disease.html", disease=disease, ai_suggestion=ai_suggestion)
    else:
        return "Not Found"

@app.route('/chat', methods=['GET'])
def get_chat():
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            "You a disease diagnosing staff",
            "Create a basic diagnosis for a patient with the following symptoms: black skin spots, swelling, fever, vomiting, and headache.",
            "The patient have been experiencing the symptoms for a week already",
            "Provide an accurate diagnosis"
        ]
    )
    return response.text

@app.route('/diagnosis', methods=['GET'])
def get_diagnosis():
    symptoms = request.args.get('symptoms', '').lower()
    matches = generate_diagnosis(symptoms)
    return jsonify(matches)

if __name__ == "__main__":
    app.run(debug=True)