from flask import Flask, jsonify, redirect, url_for, request, render_template
import json
import os

# Load the JSON file
with open('diseases.json', encoding="utf-8") as file:  # Works cross-platform
    data = json.load(file)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diseases')
def diseases():
    return jsonify(data)
@app.route('/search_disease', methods=['POST'])
def search_disease():
    query = request.json.get('query', '').strip().lower()
    
    if not query:
        return jsonify({'error': 'Search keyword is required'}), 400

    # Find all diseases that match the search term
    matches = [disease for disease in data if query in disease["primary_name"].lower()]

    if matches:
        return jsonify(matches)
    else:
        return jsonify({'error': 'No diseases found'}), 404

@app.route('/disease/<key_id>')
def get_disease(key_id):
    disease_info = next((d for d in data if d["key_id"] == key_id), None)

    if disease_info:
        # Ensure word_synonyms is a list
        if "word_synonyms" in disease_info and isinstance(disease_info["word_synonyms"], str):
            disease_info["word_synonyms"] = disease_info["word_synonyms"].split(";")

        return render_template('disease_details.html', disease=disease_info)
    else:
        return "Disease not found", 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=10000)