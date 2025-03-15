from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv, dotenv_values
import google.generativeai as genai
import json
import os

# Load environment variables
load_dotenv()
config = dotenv_values(os.path.join(os.path.dirname(__file__), ".env"))

app = Flask(__name__, template_folder="templates", static_folder="static")

# Load diseases data
with open(os.path.join(os.path.dirname(__file__), 'diseases.json')) as f:
    diseases = json.load(f)

# Initialize Gemini AI Client
client = genai.Client(api_key=config['GEMINI_API_KEY'])

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["GET"])
def search_diseases():
    """Search for diseases by name, synonyms, or AI-powered matching"""
    query = request.args.get("q", "").strip().lower()
    if not query:
        return render_template("results.html", matches=[], query=query)

    # Call AI-powered diagnosis
    ai_matches = []
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                "This is the existing data in JSON format: " + json.dumps(diseases),
                f"Match the closest disease with the following symptom: {query}",
                "Include the info_link_data in the response.",
                "Return the top three matching diseases.",
                "Give me a short description of each.",
                "Give me suggestions for alleviating symptoms of each."
            ],
            config={"response_mime_type": "application/json"}
        )
        ai_matches = json.loads(response.text)  # Convert AI response to JSON
        print("AI Matches:", ai_matches)  # Debugging log
    except (json.JSONDecodeError, KeyError) as e:
        print("Error decoding AI response:", e)  # Debugging log
        ai_matches = []  # Handle AI response errors

    # If AI search fails, use manual search as a fallback
    if not ai_matches:
        ai_matches = [
            {
                "key_id": disease["key_id"],
                "primary_name": disease["primary_name"],
                "is_procedure": bool(disease.get("is_procedure", False)),
                "synonyms": disease.get("synonyms", []),
                "icd10cm": disease.get("icd10cm", []),
                "info_links": disease.get("info_link_data", []),
                "description": "No description available.",
                "suggestions": "No suggestions available."
            }
            for disease in diseases
            if query in disease["primary_name"].lower()
            or any(query in synonym.lower() for synonym in disease.get("synonyms", []))
        ]

    return render_template("results.html", matches=ai_matches, query=query)

if __name__ == "__main__":
    app.run(debug=True)
