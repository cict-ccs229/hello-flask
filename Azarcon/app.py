from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)

# Load diseases data
with open(os.path.join(os.path.dirname(__file__), 'diseases.json')) as f:
    diseases = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/match', methods=['POST'])
def match_diseases():
    symptoms = request.form.get('symptoms', '').lower().split(',')
    matched_diseases = []

    for disease in diseases:
        disease_symptoms = disease.get('synonyms', [])
        if any(symptom.strip() in disease_symptoms for symptom in symptoms):
            matched_diseases.append(disease['primary_name'])

    return jsonify(matched_diseases)

@app.route('/lookup', methods=['POST'])
def lookup_disease():
    query = request.form.get('query', '').lower()
    results = []

    for disease in diseases:
        if query in disease.get('primary_name', '').lower() or query in disease.get('icd10cm_codes', '').lower():
            results.append({
                'primary_name': disease.get('primary_name'),
                'synonyms': disease.get('synonyms', []),
                'info_links': disease.get('info_link_data', []),
                'icd10cm_codes': disease.get('icd10cm_codes', ''),
                'is_procedure': disease.get('is_procedure', False)
            })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)