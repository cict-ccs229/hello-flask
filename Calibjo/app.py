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

load_dotenv()

config = dotenv_values(".env")

client = genai.Client(api_key=config['GEMINI_API_KEY'])

app = Flask(__name__)

diseases = []

# Load data from diseases.json file
with open('diseases.json') as f:
    diseases = json.load(f)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/diseases', methods=['GET'])
def get_diseases():
    return jsonify(diseases)

@app.route('/chat', methods=['GET'])
def get_chat():
    response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        "You a disease diagnosing staff",
        "Create a basic diagnosis for a patient with the following symptoms: black skin spots, swelling, fever, vomiting, and headache.",
        "The patient have been experiencing the symptoms for a week already",
        "Provide an accurate diagnosis"
    ])
    return response.text

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

if __name__ == '__main__':
    app.run(debug=True)      