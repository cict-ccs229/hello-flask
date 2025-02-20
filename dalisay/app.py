from flask import Flask
import os, json, re

def main():
  app = Flask(__name__)
  icd_9_file = os.path.join(os.getcwd(), 'diseases.json') # This is meant to be run from the root directory
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

  app.run(port=5000)

if __name__ == '__main__':
    main()