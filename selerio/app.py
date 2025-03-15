import os
import json
import re
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv, dotenv_values
import google.generativeai as genai

# Load environment variables
load_dotenv()
config = dotenv_values(".env")

genai.configure(api_key=config['GEMINI_API_KEY'])

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of app.py
JSON_PATH = os.path.join(BASE_DIR, "diseases.json")  # Construct the absolute path

with open(JSON_PATH, "r") as file:
    diseases = json.load(file)

# Load JSON data
with open("diseases.json", "r") as file:
    diseases = json.load(file)

@app.route("/")
def home():
    """Serve the frontend"""
    return render_template("index.html")

@app.route("/search", methods=["GET"])
def search_diseases():
    """Search for diseases by name or synonyms"""
    query = request.args.get("q", "").strip().lower()
    if not query:
        return jsonify([])

    results = []
    
    for disease in diseases:
        name_match = query in disease["primary_name"].lower()
        synonym_match = any(query in synonym.lower() for synonym in disease.get("synonyms", []))

        if name_match or synonym_match:
            results.append({
                "key_id": disease["key_id"],
                "primary_name": disease["primary_name"],
                "is_procedure": bool(disease.get("is_procedure", False)),  
                "synonyms": disease.get("synonyms", []),
                "icd10cm": disease.get("icd10cm", []),
                "info_links": disease.get("info_link_data", [])
            })

    return jsonify(results)

@app.route("/gemini-response", methods=["GET"])
def gemini_response():
    """Generate disease details using Gemini"""
    key_id = request.args.get("key_id", "").strip()
    
    if not key_id:
        return jsonify({"error": "No key_id provided"}), 400

    # Find the disease by key_id
    disease = next((d for d in diseases if d["key_id"] == key_id), None)
    
    if not disease:
        return jsonify({"error": "Disease not found"}), 404

    try:
        # Initialize the generative model
        model = genai.GenerativeModel('gemini-1.5-flash-latest')  

        # Generate content
        response = model.generate_content(
            f"Provide detailed information about the following disease: {disease['primary_name']}\n"
            "Return the response in valid JSON format with these fields:\n"
            "- primary_name: The name of the disease\n"
            "- description: A brief overview of the disease in 3 sentences\n"
            "- symptoms: Common symptoms associated with the disease in 2 sentences\n"
            "- treatment: Effective treatments or remedies in 5 sentences\n"
        )

        raw_response = response.text
        print("AI Raw Response:", raw_response)  # Debugging output

        # Remove markdown formatting if present
        cleaned_response = re.sub(r"```json\s*([\s\S]*?)\s*```", r"\1", raw_response).strip()

        try:
            disease_data = json.loads(cleaned_response)
            return jsonify(disease_data)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid response from AI", "raw_response": cleaned_response}), 500

    except Exception as e:
        return jsonify({"error": f"Failed to generate response: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
