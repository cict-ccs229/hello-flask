from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv, dotenv_values
from google import genai
from pydantic import BaseModel
import json
import os
import requests

app = Flask(__name__)

def load_diseases():
    with open("diseases.json", "r") as file:
        data = json.load(file)
        return {
            item["key_id"]: {
                "name": item["primary_name"],
                "icd10cm_codes": ", ".join(code["code"] for code in item.get("icd10cm", [])),
                "icd10cm_text": ", ".join(code["name"] for code in item.get("icd10cm", [])),
                "info_link": item["info_link_data"][0][0] if item.get("info_link_data") else "#"
            }
            for item in data
        }

diseases = load_diseases()
load_dotenv()
config = dotenv_values(".env")
client = genai.Client(api_key=config['GEMINI_API_KEY'])

@app.route("/")
def index():
    return render_template("index.html", diseases=diseases)

@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    filtered_diseases = {
        key: value for key, value in diseases.items()
        if query in key.lower()  # Search by ID
        or query in value["name"].lower()  # Search by Name
        or query in value["icd10cm_codes"].lower()  # Search by ICD-10 Codes
    }
    return jsonify(filtered_diseases)

if __name__ == "__main__":
    app.run(debug=True)
