from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Load the data from the JSON file
json_path = os.path.join(os.path.dirname(__file__), 'diseases.json')
with open(json_path) as file:
    data = json.load(file)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Diseases and Procedures API! Use the endpoints below for more details.",
                    "endpoints": {
                        "/info/<key_id>": "Get information for a specific key_id.",
                        "/search": "Search diseases or procedures by name or keyword.",
                        "/categories": "List all unique categories (disease/procedure).",
                        "/all": "Retrieve all diseases and procedures data."
                    }})

@app.route('/info/<key_id>', methods=['GET'])
def get_info(key_id):
    """Fetch information by key_id."""
    result = next((item for item in data if item['key_id'] == key_id), None)
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "No information found for the given key_id."}), 404

@app.route('/search', methods=['GET'])
def search():
    """Search diseases or procedures by primary name, synonyms, or keywords."""
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify({"error": "Query parameter is required."}), 400

    results = [
        item for item in data
        if query in item['primary_name'].lower() or
           any(query in synonym.lower() for synonym in item.get('synonyms', [])) or
           query in item.get('word_synonyms', '').lower()
    ]
    return jsonify(results if results else {"message": "No results found."})

@app.route('/categories', methods=['GET'])
def list_categories():
    """List unique categories: disease or procedure."""
    categories = {
        "Diseases": len([item for item in data if not item['is_procedure']]),
        "Procedures": len([item for item in data if item['is_procedure']])
    }
    return jsonify(categories)

@app.route('/all', methods=['GET'])
def get_all():
    """Retrieve all diseases and procedures."""
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
