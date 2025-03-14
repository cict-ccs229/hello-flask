from flask import Flask, request, jsonify, render_template
import json

app = Flask(__name__)

with open("diseases.json", "r") as f:
    diseases = json.load(f)


# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/diagnosis", methods=["GET"])
def find_disease():
    symptoms = request.args.get("symptoms", "").lower().split(",")
    results = []

    for disease in diseases:
        word_synonyms = disease.get("word_synonyms", "").lower()
        synonyms = [synonym.lower() for synonym in disease.get("synonyms", [])]

        symptoms = [s.strip() for s in symptoms]

        if any(
            symptom in word_synonyms or 
            symptom in synonyms
            for symptom in symptoms
        ):
            results.append({
                "name": disease["primary_name"],
                "icd10_codes": disease.get("icd10cm_codes", "N/A"),
                "info_link": disease["info_link_data"][0][0] if disease.get("info_link_data") else "N/A"
            })

    print(symptoms, results)

    return jsonify(results if results else ({"message": "No matching diseases found"}, 404))

if __name__ == "__main__":
    app.run(debug=True)