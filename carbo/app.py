from flask import Flask, jsonify, render_template_string
import json
import os

app = Flask(__name__)

with open('diseases.json') as f:
    diseases = json.load(f)

@app.route('/')
def home():
    with open(os.path.join(os.path.dirname(__file__), 'index.html')) as f:
        html_content = f.read()
    return render_template_string(html_content)

@app.route('/diseases', methods=['GET'])
def get_diseases():
    return jsonify(diseases)

if __name__ == '__main__':
    app.run(debug=True)