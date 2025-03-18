from flask import Flask, render_template, request
import json

app = Flask(__name__, template_folder="frontend", static_folder="assets")

def load_diseases():
    with open("diseases.json", encoding="utf-8") as file:
        return json.load(file)

diseases = load_diseases()

@app.route("/", methods=["GET", "POST"])
def index():
    user_symptom = None
    matched_diseases = []
    disease_data = None

    if request.method == "POST":
        user_symptom = request.form.get("symptom", "").strip().lower()
        matched_diseases = [d for d in diseases if user_symptom in d.get("word_synonyms", "").lower() or 
                             any(user_symptom in synonym.lower() for synonym in d.get("synonyms", []))]
    
    disease_id = request.args.get("disease_id")
    if disease_id:
        disease_data = next((d for d in diseases if d["key_id"] == disease_id), None)
    
    return render_template("index.html", symptom=user_symptom, diseases=matched_diseases, disease=disease_data)

if __name__ == "__main__":
    app.run(debug=True)
