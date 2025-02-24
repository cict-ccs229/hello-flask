from flask import Flask, request, jsonify, render_template
import json, os

# initialization
app = Flask(__name__, template_folder='frontend')

# Load diseases data from JSON file
current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "diseases.json")

with open(json_path, "r") as file:
    diseases = json.load(file)

# render the html
@app.route("/")
def index():
    return render_template("index.html")

# query for the possible disease based on input
@app.route("/diagnosis", methods=["GET", "POST"])
def get_disease():
    if request.method == "POST":
        symptoms = request.form.get("symptoms", "").lower()
    else:
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
                        "primary_name": disease["primary_name"],
                        "icd10_codes": disease.get("icd10cm_codes", "N/A"),
                        "info_link": disease["info_link_data"][0][0] if disease.get("info_link_data") else "N/A",
                        "synonyms": disease.get("synonyms", []),
                        "term_icd9_text": disease.get("term_icd9_text", None),
                        "info_link_data": disease.get("info_link_data", [])
                    })

    if not results:
        return render_template("disease.html", diseases=[], message="No matching diseases found")

    return render_template("disease.html", diseases=results)


if __name__ == "__main__":
    app.run(debug=True)