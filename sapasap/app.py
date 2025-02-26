from flask import Flask, render_template, request, jsonify
import json
import os


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "frontend"))

json_path = os.path.join(BASE_DIR, "diseases.json")
with open(json_path, encoding="utf-8") as f:
    diseases_data = json.load(f)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        symptom = request.form.get("symptom").lower()
        matches = [
            disease for disease in diseases_data
            if symptom in disease.get("word_synonyms", "").lower() or
               any(symptom in syn.lower() for syn in disease.get("synonyms", []))
        ]
        return render_template("results.html", matches=matches, symptom=symptom)
    return render_template("index.html")

@app.route("/disease/<disease_id>")
def disease_details(disease_id):
    disease = next((d for d in diseases_data if d["key_id"] == disease_id), None)
    return render_template("disease.html", disease=disease) if disease else "Not Found"

if __name__ == "__main__":
    app.run(debug=True)
