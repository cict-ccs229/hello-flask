import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv, dotenv_values
import json
import re
import google.generativeai as genai
from pydantic import BaseModel

class Diagnosis(BaseModel):
    key_id: str
    primary_name: str
    consumer_name: str
    word_synonyms: str
    synonyms: list[str]
    info_link_data: list[list[str]]

# Load API key
load_dotenv()
config = dotenv_values(".env")

# Configure generative AI
genai.configure(api_key=config['GEMINI_API_KEY'])

# Initialize Flask app
app = Flask(__name__)

# Get the absolute path to the diseases.json file
diseases_path = os.path.join(os.path.dirname(__file__), 'diseases.json')

# Load diseases data from JSON file
with open(diseases_path) as f:
    diseases = json.load(f)

@app.route("/")
def home():
    return render_template("index2.html")

@app.route('/diseases', methods=['GET'])
def get_diseases():
    return jsonify(diseases)

@app.route('/diagnosis', methods=['GET'])
def get_diagnosis():
    symptoms = request.args.get('symptoms', '').lower()

    try:
        # Initialize the generative model
        model = genai.GenerativeModel('gemini-1.5-flash-latest')  

        # Generate content
        response = model.generate_content(
            f"Here is a list of diseases and their details in JSON format: {json.dumps(diseases)}\n"
            f"Based on the following symptoms: {symptoms}\n"
            "Identify the top 3 most likely diseases and provide the following details for each:\n"
            "- primary_name: The name of the disease\n"
            "- description: A brief overview of the disease\n"
            "- causes: Common causes of the disease\n"
            "- effects: How the disease affects a person\n"
            "- remedies: Up to three effective treatments or home remedies\n"
            "- info_link_data: A list containing a URL and the title for further reading\n"
            "Return the response in valid JSON format without any additional text or markdown formatting."
        )

        raw_response = response.text
        print("AI Raw Response:", raw_response)  # Debugging output

        # Remove markdown code block formatting (```json ... ```)
        cleaned_response = re.sub(r"```json\s*([\s\S]*?)\s*```", r"\1", raw_response).strip()

        try:
            diagnosis_data = json.loads(cleaned_response)
            return jsonify(diagnosis_data)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid response from AI", "raw_response": cleaned_response}), 500

    except Exception as e:
        return jsonify({"error": f"Failed to generate response: {str(e)}"}), 500

@app.route('/symptom-suggestions', methods=['GET'])
def get_symptom_suggestions():
    query = request.args.get('query', '').lower()

    try:
        # Initialize the generative model
        model = genai.GenerativeModel('gemini-1.5-flash-latest')  # Use a faster model

        # Generate content
        response = model.generate_content(
            f"Suggest possible symptoms based on the following input: {query}\n"
            "Return a JSON array of symptom names without any additional text or markdown formatting."
        )

        raw_response = response.text
        print("AI Raw Response:", raw_response)  # Debugging output

        # Remove markdown code block formatting (```json ... ```)
        cleaned_response = re.sub(r"```json\s*([\s\S]*?)\s*```", r"\1", raw_response).strip()

        try:
            suggestions = json.loads(cleaned_response)
            return jsonify(suggestions)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid response from AI", "raw_response": cleaned_response}), 500

    except Exception as e:
        return jsonify({"error": f"Failed to generate response: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)