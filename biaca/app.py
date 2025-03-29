from flask import Flask, jsonify, request, render_template
import json
import re

app = Flask(__name__)

# Load data
with open('diseases.json', 'r') as file:
    diseases_list = json.load(file)

@app.route('/')
def home():
    return render_template('index.html')

# find disease that match in any attribute
def find_matching_diseases(selected_symptoms):
    matching_diseases = []

    for disease in diseases_list:
        # Collect all searchable attributes
        searchable_attributes = []

        if disease.get('primary_name'):
            searchable_attributes.append(disease['primary_name'].lower())

        if disease.get('word_synonyms'):
            searchable_attributes.extend(disease['word_synonyms'].lower().split(';'))

        if disease.get('synonyms'):
            searchable_attributes.extend([syn.lower() for syn in disease['synonyms']])

        if disease.get('icd10cm'):
            searchable_attributes.extend([code['code'].lower() for code in disease['icd10cm']])
      
        if disease.get('term_icd9_text'):
            searchable_attributes.append(disease['term_icd9_text'].lower())

        for symptom in selected_symptoms:
            symptom_lower = symptom.lower()
            #  regex for partial matches
            if any(re.search(re.escape(symptom_lower), attr) for attr in searchable_attributes):
                matching_diseases.append({
                    'disease_name': disease['primary_name'],
                    'icd_code': ', '.join(d['code'] for d in disease.get('icd10cm', [])),
                    'link': disease['info_link_data'][0][0] if disease.get('info_link_data') else None
                })
                break 

    return matching_diseases


@app.route('/diagnose', methods=['POST'])
def diagnose():
    data = request.json
    selected_symptoms = data.get('symptoms', [])
    other_symptom = data.get('other_symptom', '').strip()

    if other_symptom:
        selected_symptoms.append(other_symptom)

    matching_diseases = find_matching_diseases(selected_symptoms)

    if matching_diseases:
        return jsonify(matching_diseases)
    else:
        return jsonify({'message': 'No matching disease found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
