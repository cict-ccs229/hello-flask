from flask import Flask, request, jsonify, render_template
import json

# initialization
app = Flask(__name__)

# Load diseases data from JSON file
with open("diseases.json", "r") as file:
    diseases = json.load(file)

# render the html
@app.route("/")
def index():
    return render_template("index.html")

# query for the possible disease based on input
@app.route("/diagnosis", methods=["GET"])
def get_disease():
    symptoms = request.args.get("symptoms", "").lower()
    if not symptoms:
        return jsonify({"error": "Please provide symptoms parameter"}), 400

    symptom_list = symptoms.split(",")  # Allow multiple symptoms
    results = []

    for disease in diseases:
        if any(symptom.strip() in disease.get("word_synonyms", "").lower() or
               symptom.strip() in [syn.lower() for syn in disease.get("synonyms", [])]
               for symptom in symptom_list):
                    results.append({
                        "name": disease["primary_name"],
                        "icd10_codes": disease.get("icd10cm_codes", "N/A"),
                        "info_link": disease["info_link_data"][0][0] if disease.get("info_link_data") else "N/A"
                    })

    if not results:
        return jsonify({"message": "No matching diseases found"}), 404

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
