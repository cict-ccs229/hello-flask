from flask import Flask, jsonify, render_template, request
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv, dotenv_values
from google import genai
import json, os
from pydantic import BaseModel

class Diagnosis(BaseModel):
    key_id: str
    primary_name: str
    consumer_name: str
    word_synonyms: str
    synonyms: list[str]
    info_link_data: list[list[str]]
    treatments: str

dotenv_path = os.path.join(os.path.dirname(__file__), 'napud', '.env')

load_dotenv(dotenv_path)

config = dotenv_values(".env")

# Check if GEMINI_API_KEY is present in the environment variables
if "GEMINI_API_KEY" not in config:
    raise KeyError("GEMINI_API_KEY not found in environment variables")

# Initialize the Client class with the API key
client = genai.Client(api_key=config["GEMINI_API_KEY"])

# initialization
app = Flask(__name__, template_folder='frontend')

# Load diseases data from JSON file
current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "diseases.json")

with open(json_path, "r") as file:
    diseases = json.load(file)

# render the html
@app.route("/")
def home():
    return render_template("index.html")

@app.route('/diseases', methods=['GET'])
def get_diseases():
    return jsonify(diseases)

@app.route('/diagnosis', methods=['GET', 'POST'])
def get_diagnosis():
    if request.method == "POST":
        symptoms = request.form.get("symptoms", "").lower()
    else:
        symptoms = request.args.get("symptoms", "").lower()

    if not symptoms:
        return jsonify({"error": "Please provide symptoms parameter"}), 400

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                "This is the existing data in JSON format: " + json.dumps(diseases),
                "Match the closest disease with the following symptoms: " + symptoms,
                "Include the info_link_data in the response.",
                "Return the top three matching items.",
                "Read the url from the info_link_data and get the treatments for the disease.",
                "Summarize the treatments in just a single paragraph."
                "Append the summarized data in the result and store it in the 'treatements' properly."
                "Return the results."
                
            ],
            config={"response_mime_type": "application/json",
                    "response_schema": list[Diagnosis]}
        )
        return json.loads(response.text)
    except genai.errors.ClientError as e:
        return jsonify({"error": str(e)}), 429

if __name__ == '__main__':
    app.run(debug=True)