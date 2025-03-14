from flask import Flask, request, jsonify, render_template_string
import json
import os
from google import genai
from pydantic import BaseModel
from requests.exceptions import RequestException
from dotenv import load_dotenv, dotenv_values

class Disease(BaseModel):
    key_id: str
    primary_name: str
    consumer_name: str
    word_synonyms: str
    synonyms: list[str]
    info_link_data: list[list[str]]

load_dotenv()
config = dotenv_values(".env")
client = genai.Client(api_key=config['GEMINI_API_KEY'])

app = Flask(__name__)

diseases = []

# Get the directory where the script is running
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "diseases.json")

# Load the disease data from the JSON file
try:
    with open(JSON_FILE, "r") as file:
        diseases = json.load(file)
except FileNotFoundError:
    diseases = []  # If file is missing, start with an empty list

# HTML + CSS Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diseases Information</title>
    <style>
        /* General Page Styles */
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
        }
        
        /* Header Styling */
        h1 {
            text-align: center;
            color: #007bff;
        }

        /* Search Box */
        input[type="text"] {
            width: 100%;
            max-width: 400px;
            padding: 10px;
            margin: 20px auto;
            display: block;
            border: 2px solid #007bff;
            border-radius: 5px;
            font-size: 16px;
        }

        /* Search Results */
        #results {
            margin-top: 20px;
            padding: 10px;
        }

        /* Disease List */
        ul {
            list-style-type: none;
            padding: 0;
        }

        li {
            background: #fff;
            margin: 10px 0;
            padding: 15px;
            border-left: 5px solid #007bff;
            border-radius: 5px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }

        /* Links */
        a {
            color: #007bff;
            text-decoration: none;
            font-weight: bold;
        }

        a:hover {
            text-decoration: underline;
        }

        /* Responsive Design */
        @media (max-width: 600px) {
            input[type="text"] {
                width: 90%;
            }
        }
    </style>
    <script>
        function searchDisease() {
            let query = document.getElementById("search").value.toLowerCase();
            fetch(`/search?q=${query}`)
                .then(response => response.json())
                .then(data => {
                    let resultsDiv = document.getElementById("results");
                    resultsDiv.innerHTML = "";
                    if (data.length === 0) {
                        resultsDiv.innerHTML = "<p>No results found.</p>";
                    } else {
                        data.forEach(disease => {
                            let infoLink = disease.info_link_data.length ? 
                                `<a href="${disease.info_link_data[0][0]}" target="_blank">${disease.info_link_data[0][1]}</a>` 
                                : 'No Link Available';
                            resultsDiv.innerHTML += `<p><strong>${disease.primary_name}</strong> - ${infoLink}</p>`;
                        });
                    }
                });
        }
    </script>
</head>
<body>
    <h1>Diseases Information</h1>
    <input type="text" id="search" placeholder="Search for a disease..." onkeyup="searchDisease()">
    <div id="results"></div>
    
    <h2>All Diseases</h2>
    <ul>
        {% for disease in diseases %}
            <li><strong>{{ disease.primary_name }}</strong> - 
                <a href="{{ disease.info_link_data[0][0] if disease.info_link_data else '#' }}" target="_blank">
                {{ disease.info_link_data[0][1] if disease.info_link_data else 'No Link Available' }}
                </a>
            </li>
        {% endfor %}
    </ul>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, diseases=diseases)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    results = []

    for d in diseases:
        # Check if the query matches primary name, synonyms, or ICD codes
        if (query in d['primary_name'].lower() or
            any(query in syn.lower() for syn in d.get('synonyms', [])) or
            any(query in code['code'].lower() for code in d.get('icd10cm', []))):
            results.append(d)
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
