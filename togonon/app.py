from flask import Flask, render_template, request, jsonify
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Define base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend")
DATA_PATH = os.path.join(BASE_DIR, "diseases.json")

# Initialize Flask app
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder="assets")

# Load diseases JSON data
try:
    with open(DATA_PATH, encoding="utf-8") as f:
        diseases_data = json.load(f)
        print(f"✅ Loaded {len(diseases_data)} disease entries.")
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"❌ Error loading diseases.json: {e}")
    diseases_data = []

# Function to find matching diseases from JSON
def find_matching_diseases(symptom):
    if not symptom:
        return []

    symptom = symptom.lower().strip()

    # **Corrected Matching Logic**
    matching_diseases = [
        d for d in diseases_data
        if symptom in d.get("word_synonyms", "").lower() or 
           any(symptom in synonym.lower() for synonym in d.get("synonyms", []))
    ]

    print(f"🔍 Found {len(matching_diseases)} matching diseases for symptom: {symptom}")
    return matching_diseases

# Function to generate AI-based disease analysis
def generate_disease_analysis(disease_name):
    if not disease_name:
        return "No disease name provided for AI analysis."

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            f"Provide a detailed medical analysis of the disease {disease_name}, including causes, symptoms, treatments, and risk factors."
        )
        return response.text if response and response.text else "No AI-generated analysis available."
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return "Error generating AI details."

# Home route (Search for symptoms)
@app.route("/", methods=["GET", "POST"])
def index():
    symptom = None
    diseases = []
    disease_data = None
    ai_analysis = None

    if request.method == "POST":
        symptom = request.form.get("symptom", "").strip().lower()

        # **Fix: Use corrected search logic**
        diseases = find_matching_diseases(symptom)

    disease_id = request.args.get("disease_id")
    if disease_id:
        disease_data = next((d for d in diseases_data if d["key_id"] == disease_id), None)

        if disease_data:
            ai_analysis = generate_disease_analysis(disease_data["primary_name"])

    return render_template("index.html", symptom=symptom, diseases=diseases, disease=disease_data, ai_analysis=ai_analysis)

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
