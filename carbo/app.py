import os
from flask import Flask, jsonify, render_template_string, request
from dotenv import load_dotenv
import json
import re
import google.generativeai as genai

# Load API key from .env file
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

# Configure generative AI
genai.configure(api_key=api_key)

# Initialize Flask app
app = Flask(__name__)

# Load diseases data from JSON file
try:
    with open('diseases.json') as f:
        if f.read().strip():  # Check if file is not empty
            f.seek(0)  # Reset file pointer to the beginning
            diseases_data = json.load(f)
        else:
            raise ValueError("JSON file is empty")
except (json.JSONDecodeError, ValueError) as e:
    diseases_data = {"error": str(e)}

@app.route('/')
def home():
    with open('index.html') as f:
        html_content = f.read()
    return render_template_string(html_content)

@app.route('/diseases', methods=['GET'])
def list_diseases():
    return jsonify(diseases_data)

@app.route('/diagnose', methods=['GET'])
def diagnose():
    symptoms = request.args.get('symptoms', '').lower()

    try:
        # Initialize the generative model
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        # Generate content
        response = model.generate_content(
            f"This is a list of diseases and their details in JSON format: {json.dumps(diseases_data)}\n"
            f"Considering the following symptoms: {symptoms}\n"
            "Identify and choose the top 3 most likely diseases and provide the following details for each:\n"
            "- primary_name: The name of the disease\n"
            "- description: A brief overview of the disease\n"
            "- info_link_data: A list containing a URL and the title for further reading\n"
            "- doctor_response: Advice from a doctor on what the patient should do next\n"
            "Return the response in valid JSON format without any additional text or markdown formatting."
        )

        raw_response = response.text
        print("AI Raw Response:", raw_response)  # Debugging output

        # Clean the response
        cleaned_response = re.sub(r"```json\s*([\s\S]*?)\s*```", r"\1", raw_response).strip()

        try:
            diagnosis_results = json.loads(cleaned_response)
            print("Diagnosis Results:", diagnosis_results)  # Debugging output
            return jsonify(diagnosis_results)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid response from AI", "raw_response": cleaned_response}), 500

    except Exception as e:
        return jsonify({"error": f"Failed to generate response: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)