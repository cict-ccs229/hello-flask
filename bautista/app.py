from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import google.generativeai as genai 
from dotenv import load_dotenv
from pydantic import BaseModel
import os


# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Google Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Load disease dataset
with open("diseases.json") as f:
    diseases = json.load(f)

app = Flask(__name__)
CORS(app)

class Diagnosis(BaseModel):
    key_id: str
    primary_name: str
    consumer_name: str
    word_synonyms: str
    synonyms: list[str]
    info_link_data: list[list[str]]

@app.route("/")
def home():
    """Render the home page."""
    return render_template("index.html")

@app.route("/diseases", methods=["GET"])
def get_diseases():
    """Returns all diseases in the dataset."""
    return jsonify(diseases)

@app.route("/disease/<string:name>")
def disease_detail(name):
    """Render the disease detail page."""
    name_lower = name.lower()
    disease = next(
        (disease for disease in diseases if
         disease["primary_name"].lower() == name_lower or
         any(syn.lower() == name_lower for syn in disease.get("synonyms", []))),
        None
    )

    if disease:
        return render_template("disease_detail.html", disease=disease)
    return jsonify({"error": "Disease not found"}), 404

@app.route("/diagnose", methods=["GET"])
def diagnose():
    """
    Diagnose based on symptoms.
    Example: /diagnose?symptoms=fever,headache
    """
    symptoms = request.args.get("symptoms")
    if not symptoms:
        return jsonify({"error": "Please provide symptoms as a query parameter"}), 400

    symptoms_list = [s.strip().lower() for s in symptoms.split(",")]
    possible_diseases = []

    for disease in diseases:
        disease_symptoms = disease.get("word_synonyms", "").lower().split(";")  # Symptoms stored as synonyms
        synonyms_list = [syn.lower() for syn in disease.get("synonyms", [])]  # Alternative names of disease

        matches = [
            symptom for symptom in symptoms_list
            if any(symptom in word for word in disease_symptoms + synonyms_list)
        ]

        if matches:
            possible_diseases.append({
                "name": disease["primary_name"],
                "matched_symptoms": matches
            })

    if not possible_diseases:
        return jsonify({"possible_diseases": [], "message": "No matching diseases found. Try different symptoms."})

    return jsonify({"possible_diseases": possible_diseases})

@app.route('/chat', methods=['GET', 'POST'])
def get_chat():
    diagnosis = None
    if request.method == 'POST':
        symptoms = request.form.get('symptoms', '').lower()
        response = model.generate_content(
            contents=[
                f"You are a disease diagnosing staff.",
                f"Create a basic diagnosis for a patient with the following symptoms: {symptoms}.",
                "The patient has been experiencing the symptoms for a week already.",
                "Provide an accurate diagnosis."
            ]
        )
        
        # Extract only the 'text' field from the response
        if hasattr(response, 'text'):
            diagnosis = response.text.strip()
    
    return render_template('chat.html', diagnosis=diagnosis)

@app.route('/diagnosis', methods=['POST'])
def diagnosis():
    # Returns the top three matching diseases based on the symptoms
    symptoms = request.get_json()["symptoms"]
    response = client.models.generate_content(
    model="gemini-2.0-flash", 
    contents=[
        "This is the existing data in JSON format: " + json.dumps(diseases),
        "Match the closest disease with following symptoms: " + symptoms,
        "Include the info_link_data in the response.",
        "Return the top three matching items."],
    config = {
        "response_mime_type": "application/json",
        "response_schema": list[Diagnosis]},
    )
    
    return json.loads(response.text)

if __name__ == "__main__":
    app.run(debug=True)
