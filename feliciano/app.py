import os
import json
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
from pydantic import BaseModel

app = Flask(__name__)

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Google Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Load disease data
def load_diseases():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'diseases.json')
    with open(file_path, 'r') as file:
        return json.load(file)

# Home endpoint that shows the index.html page with pagination
@app.route('/')
def home():
    diseases = load_diseases()
    page = request.args.get('page', 1, type=int)  # Get current page, default is 1
    start = (page - 1) * 10
    end = start + 10
    diseases_to_show = diseases[start:end]
    
    # Calculate the total number of pages
    total_pages = (len(diseases) // 10) + (1 if len(diseases) % 10 > 0 else 0)
    
    # Generate page numbers for navigation with ellipses
    page_numbers = []
    if total_pages <= 10:
        page_numbers = list(range(1, total_pages + 1))
    else:
        if page <= 5:
            page_numbers = list(range(1, 6)) + ['...'] + [total_pages]
        elif page >= total_pages - 4:
            page_numbers = [1] + ['...'] + list(range(total_pages - 4, total_pages + 1))
        else:
            page_numbers = [1] + ['...'] + list(range(page - 2, page + 3)) + ['...'] + [total_pages]

    return render_template('index.html', diseases=diseases_to_show, page=page, total_pages=total_pages, page_numbers=page_numbers)

# Endpoint to search for diseases based on query keyword
@app.route('/search', methods=['GET'])
def search_diseases():
    query = request.args.get('query', '').lower()  # Get the query from the form
    diseases = load_diseases()
    
    # Filter diseases by matching the query with disease name or synonyms
    matching_diseases = [
        disease for disease in diseases if query in disease['primary_name'].lower() or query in disease['word_synonyms'].lower()
    ]
    
    page = request.args.get('page', 1, type=int) 
    start = (page - 1) * 10
    end = start + 10
    diseases_to_show = matching_diseases[start:end]
    
    # Calculate the total number of pages
    total_pages = (len(matching_diseases) // 10) + (1 if len(matching_diseases) % 10 > 0 else 0)
    
    # Generate page numbers for navigation with ellipses
    page_numbers = []
    if total_pages <= 10:
        page_numbers = list(range(1, total_pages + 1))
    else:
        if page <= 5:
            page_numbers = list(range(1, 6)) + ['...'] + [total_pages]
        elif page >= total_pages - 4:
            page_numbers = [1] + ['...'] + list(range(total_pages - 4, total_pages + 1))
        else:
            page_numbers = [1] + ['...'] + list(range(page - 2, page + 3)) + ['...'] + [total_pages]
    
    return render_template('index.html', diseases=diseases_to_show, page=page, total_pages=total_pages, page_numbers=page_numbers, query=query)

# Endpoint to get details about a specific disease by key_id
@app.route('/disease/<string:key_id>', methods=['GET'])
def get_disease_info(key_id):
    diseases = load_diseases()
    disease = next((d for d in diseases if d["key_id"] == key_id), None)
    
    if disease is None:
        return jsonify({"message": "Disease not found"}), 404
    
    return render_template('diseases.html', disease=disease)

# Chatbot route to generate diagnosis with confidence levels (advanced method)
@app.route('/chat_advanced', methods=['GET', 'POST'])
def chat_advanced():
    diagnosis = None
    if request.method == 'POST':
        symptoms = request.form.get('symptoms', '').lower()

        # Generate diagnosis with confidence levels using the advanced method
        response = model.generate_content([
            f"This is the existing data in JSON format: {json.dumps(load_diseases())}",
            f"Match the closest disease with the following symptoms: {symptoms}",
            "Provide the most likely disease with a confidence percentage.",
            "List the next three closest diseases with their confidence levels.",
            "Include the info_link_data for all matches in the response."
        ])

        # Process response
        if hasattr(response, 'text'):
            diagnosis = format_diagnosis(response.text.strip())
            print("Gemini Response:", diagnosis)
    
    return render_template('chat_advanced.html', diagnosis=diagnosis)

# Function to format the diagnosis response into HTML
def format_diagnosis(raw_text):
    formatted_html = f"""
    <h1>Preliminary Diagnosis</h1>
    <p><strong>Important Note:</strong> This is a basic, <em>preliminary</em> diagnosis based on the symptom of fever that has persisted for one week. It is <strong>not</strong> a substitute for a professional medical evaluation.</p>
    
    <h2>Most Likely Disease</h2>
    <p><strong>Primary Diagnosis:</strong> {raw_text.splitlines()[0]}</p> <!-- Assuming first line of response is the most likely disease -->
    
    <h3>Confidence Level:</h3>
    <p><strong>Confidence:</strong> 85%</p> <!-- Example confidence level, adjust accordingly based on the response -->
    
    <h2>Next Closest Diseases</h2>
    <ul>
        <li><strong>Disease 1:</strong> Details with confidence percentage</li>
        <li><strong>Disease 2:</strong> Details with confidence percentage</li>
        <li><strong>Disease 3:</strong> Details with confidence percentage</li>
    </ul>
    <h3>Information Links</h3>
    <ul>
        <li><a href="#">Link to Disease 1</a></li>
        <li><a href="#">Link to Disease 2</a></li>
        <li><a href="#">Link to Disease 3</a></li>
    </ul>
    """
    return formatted_html

# Chatbot route to generate basic diagnosis (original method)
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    diagnosis = None
    if request.method == 'POST':
        symptoms = request.form.get('symptoms', '').lower()

        # Generate basic diagnosis using the original method
        response = model.generate_content([ 
            "You are a disease diagnosing staff.",
            f"Create a basic diagnosis for a patient with the following symptoms: {symptoms}.",
            "The patient has been experiencing the symptoms for a week already.",
            "Provide an accurate diagnosis."
        ])

        # Process response
        if hasattr(response, 'text'):
            diagnosis = response.text.strip()
            print("Gemini Response:", diagnosis)
    
    return render_template('chat.html', diagnosis=diagnosis)

if __name__ == '__main__':
    app.run(debug=True)
