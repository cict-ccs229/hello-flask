from flask import Flask, jsonify, request, render_template
import json
import re
from chat import chat_bp  # Import the chatbot Blueprint

app = Flask(__name__)

# Register Blueprint for chatbot
app.register_blueprint(chat_bp, url_prefix='/chat')

# Load diseases data safely
try:
    with open('diseases.json', 'r') as file:
        diseases_list = json.load(file)
except FileNotFoundError:
    diseases_list = []

@app.route('/')
def home():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/chat')
def chat_page():
    """Render the chatbot interface."""
    return render_template('chat.html')

# Function to find matching diseases based on symptoms
def find_matching_diseases(selected_symptoms):
    matching_diseases = []

    for disease in diseases_list:
        searchable_attributes = set()

        if disease.get('primary_name'):
            searchable_attributes.add(disease['primary_name'].lower())

        if disease.get('word_synonyms'):
            searchable_attributes.update(disease['word_synonyms'].lower().split(';'))

        if disease.get('synonyms'):
            searchable_attributes.update([syn.lower() for syn in disease['synonyms']])

        if disease.get('icd10cm'):
            searchable_attributes.update([code['code'].lower() for code in disease['icd10cm']])

        if disease.get('term_icd9_text'):
            searchable_attributes.add(disease['term_icd9_text'].lower())

        # Check if any symptom matches
        for symptom in selected_symptoms:
            symptom_lower = symptom.lower()
            if any(re.search(re.escape(symptom_lower), attr) for attr in searchable_attributes):
                matching_diseases.append({
                    'disease_name': disease['primary_name'],
                    'icd_code': ', '.join(d['code'] for d in disease.get('icd10cm', [])),
                    'link': disease['info_link_data'][0][0] if disease.get('info_link_data') else None
                })
                break  # Stop after the first match to prevent duplicates

    return matching_diseases

@app.route('/diagnose', methods=['POST'])
def diagnose():
    """Diagnose diseases based on provided symptoms."""
    data = request.json
    selected_symptoms = data.get('symptoms', [])
    other_symptom = data.get('other_symptom', '').strip()

    if not selected_symptoms and not other_symptom:
        return jsonify({'error': 'No symptoms provided'}), 400

    if other_symptom:
        selected_symptoms.append(other_symptom)

    matching_diseases = find_matching_diseases(selected_symptoms)

    if matching_diseases:
        return jsonify(matching_diseases)
    else:
        return jsonify({'message': 'No matching disease found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
