import os, json, re

from flask import Flask, request
from dotenv import dotenv_values
from pydantic import BaseModel
from google import genai

class Diagnosis(BaseModel):
  key_id: str
  primary_name: str
  consumer_name: str
  word_synonyms: str
  synonyms: list[str]
  info_link_data: list[list[str]]
  treatments: str

def create_app():
  app = Flask(__name__)

  if (os.path.exists(os.path.join(os.getcwd(), ".env"))):
    env = dotenv_values(os.path.join(os.getcwd(), ".env"))
    client = genai.Client(api_key=env["GENAI_API_KEY"])
  else:
    client = genai.Client(api_key=os.environ.get("GENAI_API_KEY"))

  icd_9_file = os.path.join(os.getcwd(), '..', 'diseases.json') # This is meant to be run from the root directory
  icd_9_json = open(icd_9_file).read()

  icd_9_arr = json.loads(icd_9_json)
  icd_9_diseases = []
  icd_9_procedures = []

  for row in icd_9_arr:
    if row["is_procedure"] == False:
      icd_9_diseases.append(row)
    else:
      icd_9_procedures.append(row)

  @app.route('/')
  def index():
    return 'Welcome to the ICD-9 Database! Change address to /disease/[name] or /procedure/[name] to search for a disease or procedure.'

  @app.route('/diseases')
  def diseases():
    # Returns a list of all diseases
    return icd_9_diseases

  @app.route('/disease/<string:name>')
  def disease(name):
    # Returns the disease that matches the name
    for row in icd_9_diseases:
      disease = re.sub(r"[\(\/ ] ?", "-", re.sub(r"[\_\)\-]", "",row["primary_name"]))
      if re.search(name, disease, re.IGNORECASE):
        return row
    return 'Disease not found.'

  @app.route('/procedures')
  def procedures():
    # Returns a list of all procedures
    return icd_9_procedures

  @app.route('/procedure/<string:name>')
  def procedure(name):
    # Returns the procedure that matches the name
    for row in icd_9_procedures:
      procedure = re.sub(r"[\(\/ ] ?", "-", re.sub(r"[\_\)\-]", "",row["primary_name"]))
      if re.search(name, procedure, re.IGNORECASE):
        return row
    return 'Procedure not found.'

  @app.route('/chat', methods=['POST'])
  def chat():
    # Returns the response from the Gemini 2.0 Flash model
    request.content_length = int(request.headers['Content-Length'])
    data = request.get_json()
    message = data["message"]
    response = client.models.generate_content(model="gemini-2.0-flash", contents=[message])
    return response.text
  
  @app.route('/diagnosis', methods=['POST'])
  def diagnosis():
    # Returns the top three matching diseases based on the symptoms
    symptoms = request.get_json()["symptoms"]
    response = client.models.generate_content(
      model="gemini-2.0-flash", 
      contents=[
        "This is the existing data in JSON format: " + json.dumps(icd_9_diseases),
        "Match the symptoms to the closest disease based on the data.",
        "The symptoms are: " + symptoms,
        "Include the information link data in the response.",
        "Read the url from the data and get the treatments for the disease.",
        "Summarize the treatments in just a single paragraph.",
        "Append the summarized treatments to the response and store it in the 'treatments' property.",
        "Return the top three matching items."],
      config = {
        "response_mime_type": "application/json",
        "response_schema": list[Diagnosis]},
      )
    
    return json.loads(response.text)
  
  return app

api = create_app()