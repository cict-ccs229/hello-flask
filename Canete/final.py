from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv, dotenv_values
import json
import re
from google import genai
from pydantic import BaseModel

class Diagnosis(BaseModel):
    key_id: str
    primary_name: str
    consumer_name: str
    word_synonyms: str
    synonyms: list[str]
    info_link_data: list[list[str]]
    remedy: str  # Added remedy field

# Load API key
load_dotenv()
config = dotenv_values(".env")
client = genai.Client(api_key=config['GEMINI_API_KEY'])

# Initialize Flask app
app = Flask(__name__)

# Load diseases data from JSON file
with open('diseases.json') as f:
    diseases = json.load(f)

@app.route("/")
def home():
    return render_template("index2.html")

@app.route('/diseases', methods=['GET'])
def get_diseases():
    return jsonify(diseases)

@app.route('/diagnosis', methods=['GET'])
def get_diagnosis():
    symptoms = request.args.get('symptoms', '').lower()

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            f"This is the existing disease data in JSON format: {json.dumps(diseases)}",
            f"Match the closest disease with the following symptoms: {symptoms}",
            "For each disease, return the following details in valid JSON format without markdown formatting:",
            "- primary_name: The name of the disease",
            "- description: A brief overview of the disease",
            "- causes: Common causes of the disease",
            "- effects: How the disease affects a person",
            "- remedies: Up to three effective treatments or home remedies",
            "- info_link_data: A list containing a URL and the title for further reading",
            "Return the top three matching diseases."
        ]
    )

    raw_response = response.text
    print("AI Raw Response:", raw_response)  # Debugging output

    # Remove markdown code block formatting (```json ... ```)
    cleaned_response = re.sub(r"```json\s*([\s\S]*?)\s*```", r"\1", raw_response).strip()

    try:
        diagnosis_data = json.loads(cleaned_response)
        return jsonify(diagnosis_data)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid response from AI", "raw_response": cleaned_response}), 500

@app.route('/symptom-suggestions', methods=['GET'])
def get_symptom_suggestions():
    query = request.args.get('query', '').lower()

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            f"Suggest possible symptoms based on the following input: {query}",
            "Return a JSON array of symptom names without any additional text or markdown formatting."
        ]
    )

    raw_response = response.text
    print("AI Raw Response:", raw_response)  # Debugging output

    # Remove markdown code block formatting (```json ... ```)
    cleaned_response = re.sub(r"```json\s*([\s\S]*?)\s*```", r"\1", raw_response).strip()

    try:
        suggestions = json.loads(cleaned_response)
        return jsonify(suggestions)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid response from AI", "raw_response": cleaned_response}), 500

if __name__ == '__main__':
    app.run(debug=True)