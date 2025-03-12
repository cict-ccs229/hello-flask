from flask import Flask, jsonify, render_template_string
import json
import os
import gemini  # Import the Gemini package

app = Flask(__name__)

with open('diseases.json') as f:
    diseases = json.load(f)

# Initialize the Gemini client
gemini_client = gemini.Client(api_key='AIzaSyCfE5FAriajahIbN6QMpLMQUeu-o3rGO4Y')

@app.route('/')
def home():
    with open(os.path.join(os.path.dirname(__file__), 'index.html')) as f:
        html_content = f.read()
    return render_template_string(html_content)

@app.route('/diseases', methods=['GET'])
def get_diseases():
    return jsonify(diseases)

@app.route('/gemini', methods=['GET'])
def get_gemini_data():
    # Example of fetching data from Gemini API
    gemini_data = gemini_client.get_data()
    return jsonify(gemini_data)

if __name__ == '__main__':
    app.run(debug=True)