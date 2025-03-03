from flask import Flask, jsonify, request, render_template
import json

from google import genai

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(debug=True)