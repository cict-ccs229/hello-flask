from flask import Flask, render_template, request
import json
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Explicitly load the .env file (adjust the path if necessary)
load_dotenv("D:/Togonon/hello-flask/togonon/.env")

# Retrieve the API key using os.getenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

class Diagnosis(BaseModel):
    key_id: str
    primary_name: str
    consumer_name: str
    word_synonyms: str 
    synonyms: list[str]
    info_link_data: list[list[str]]

app = Flask(__name__, template_folder="frontend", static_folder="assets")

def load_diseases():
    with open("togonon/diseases.json", encoding="utf-8") as file:
        return json.load(file)

diseases = load_diseases()

@app.route("/", methods=["GET", "POST"])
def index():
    user_symptom = None
    matched_diseases = []
    disease_data = None
    ai_response = None  # Store Gemini response

    if request.method == "POST":
        user_symptom = request.form.get("symptom", "").strip().lower()
        matched_diseases = [d for d in diseases if user_symptom in d.get("word_synonyms", "").lower() or 
                             any(user_symptom in synonym.lower() for synonym in d.get("synonyms", []))]

        # Use Google Gemini AI
        model = genai.GenerativeModel("gemini-2.0-flash")  
        response = model.generate_content(f"What can you tell me about the symptom: {user_symptom}?")
        ai_response = response.text if response else "No AI response available."

    disease_id = request.args.get("disease_id")
    if disease_id:
        disease_data = next((d for d in diseases if d["key_id"] == disease_id), None)
    
    return render_template("index.html", symptom=user_symptom, diseases=matched_diseases, disease=disease_data, ai_response=ai_response)

if __name__ == "__main__":
    app.run(debug=True)
