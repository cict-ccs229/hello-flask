from flask import Flask, render_template, request
import json

app = Flask(__name__)

# Load the diseases data from the JSON file
with open("diseases.json", "r") as f:
    diseases_data = json.load(f)


def search_diseases(query):
    """Searches the diseases data for entries matching the query."""
    results = []
    for disease in diseases_data:
        if (query.lower() in disease['primary_name'].lower() or
            query.lower() in disease['consumer_name'].lower() or
            any(query.lower() in syn.lower() for syn in disease['synonyms']) or
            any(query.lower() in symptom.lower() for symptom in disease.get('symptoms', []))):
            results.append(disease)
    return results


@app.route("/", methods=['GET', 'POST'])
def index():
    """Handles the main page with search functionality."""
    results = []
    query = None  # Initialize query

    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            results = search_diseases(query)
            return render_template('results.html', results=results, query=query)  # Redirect to results page

    return render_template('index.html', results=results, query=query)


@app.route("/details/<key_id>")
def details(key_id):
    """Displays details of a specific disease based on key_id."""
    disease = next((d for d in diseases_data if d['key_id'] == key_id), None)

    if disease:
        return render_template('details.html', disease=disease)
    else:
        return "Disease not found", 404

if __name__ == '__main__':
    app.run(debug=True)  # Disable debug mode in production!