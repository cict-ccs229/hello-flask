from flask import Flask, request, jsonify, render_template
import json
from google import genai
import os
from dotenv import load_dotenv, dotenv_values

# Initialization
app = Flask(__name__)
load_dotenv(dotenv_path="malatuba/.env")

# Load diseases data from JSON file
with open("diseases.json", "r") as file:
    diseases = json.load(file)

# Set up Gemini AI
config = dotenv_values(".env")
client = genai.Client(api_key=config["GENAI_API_KEY"])

# Render the HTML
@app.route("/")
def index():
    return render_template("index.html")


# Query for possible disease based on input
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


# Gemini AI Response
@app.route("/gemini", methods=["POST"])
def get_gemini_response():
    data = request.get_json()
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"response": "No input provided"})
    diseases_info = json.dumps(diseases)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            f"You are a medical assistant that provides disease diagnosis. "
            f"Use the following JSON data as reference:\n{diseases_info}\n"
            f"User symptoms: {user_message}\n"
            f"Provide a possible diagnosis with reasoning."
        ]
    )
    return jsonify({"response": response.text})


if __name__ == "__main__":
    app.run(debug=True)
