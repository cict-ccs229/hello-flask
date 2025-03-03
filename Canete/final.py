from flask import Flask, jsonify, render_template, request
from flask_caching import Cache
from concurrent.futures import ThreadPoolExecutor
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv, dotenv_values
import os

load_dotenv()
config = dotenv_values(".env")

genai.configure(api_key=config['GEMINI_API_KEY'])

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
executor = ThreadPoolExecutor(max_workers=4)

diseases_path = os.path.join(os.path.dirname(__file__), 'diseases.json')
with open(diseases_path) as f:
    diseases = json.load(f)

@app.route("/")
def home():
    return render_template("index2.html")

@app.route('/diseases', methods=['GET'])
def get_diseases():
    return jsonify(diseases)

@app.route('/diagnosis', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_diagnosis():
    symptoms = request.args.get('symptoms', '').lower()
    future = executor.submit(generate_diagnosis, symptoms)
    diagnosis_data = future.result()
    return jsonify(diagnosis_data)

def generate_diagnosis(symptoms):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
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
        cleaned_response = re.sub(r"```json\s*([\s\S]*?)\s*```", r"\1", raw_response).strip()
        diagnosis_data = json.loads(cleaned_response)
        return diagnosis_data
    except Exception as e:
        return {"error": f"Failed to generate response: {str(e)}"}

@app.route('/symptom-suggestions', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_symptom_suggestions():
    query = request.args.get('query', '').lower()
    future = executor.submit(generate_symptom_suggestions, query)
    suggestions = future.result()
    return jsonify(suggestions)

def generate_symptom_suggestions(query):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(
            f"Suggest possible symptoms based on the following input: {query}\n"
            "Return a JSON array of symptom names without any additional text or markdown formatting."
        )
        raw_response = response.text
        cleaned_response = re.sub(r"```json\s*([\s\S]*?)\s*```", r"\1", raw_response).strip()
        suggestions = json.loads(cleaned_response)
        return suggestions
    except Exception as e:
        return {"error": f"Failed to generate response: {str(e)}"}

if __name__ == '__main__':
    app.run(debug=True)