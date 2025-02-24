from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Load diseases data
with open("diseases.json") as f:
    diseases = json.load(f)

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
    # Search for disease in the diseases list
    name_lower = name.lower()
    disease = next(
        (disease for disease in diseases if
         disease["primary_name"].lower() == name_lower or
         any(syn.lower() == name_lower for syn in disease.get("synonyms", []))),
        None
    )
    
    return render_template("disease_detail.html", disease=disease)

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

        # If at least one symptom matches, add disease
        if matches:
            possible_diseases.append({
                "name": disease["primary_name"],
                "matched_symptoms": matches  # Show which symptoms matched
            })

    if not possible_diseases:
        return jsonify({"possible_diseases": [], "message": "No matching diseases found. Try different symptoms."})

    return jsonify({"possible_diseases": possible_diseases})

if __name__ == "__main__":
    app.run(debug=True)