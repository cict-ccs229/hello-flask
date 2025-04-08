from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv, dotenv_values
import google.generativeai as genai
import json
import os

# Load environment variables
load_dotenv()
api_key = os.environ.get('GEMINI_API_KEY')

app = Flask(__name__, template_folder="templates", static_folder="static")

# Load diseases data
with open(os.path.join(os.path.dirname(__file__), 'diseases.json')) as f:
    diseases = json.load(f)

# Configure Gemini AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["GET"])
def search_diseases():
    """Search for diseases by AI-powered matching"""
    query = request.args.get("q", "").strip().lower()
    if not query:
        return render_template("results.html", matches=[], query=query)

    # Call AI-powered diagnosis
    ai_matches = []
    try:
        response = model.generate_content(
            f"Given the symptom(s): '{query}', identify the top 3 possible diseases.\n"
            "Format your response strictly as a JSON array with this structure:\n"
            "[\n"
            "  {\n"
            '    "primary_name": "Disease Name",\n'
            '    "description": "Short description of the disease.",\n'
            '    "suggestions": "Ways to alleviate symptoms."\n'
            "  },\n"
            "  ... (3 diseases in total)\n"
            "]\n"
            "Do not include extra text, explanations, or markdown formatting."
        )

        print("Raw AI Response:", response.text)  # Debugging output

        ai_matches = json.loads(response.text)

        if not ai_matches:
            print("AI returned an empty list.")
            return render_template("results.html", matches=[], query=query)

        # Ensure proper formatting
        for match in ai_matches:
            match.setdefault("description", "No description available.")
            match.setdefault("suggestions", "No suggestions available.")

    except json.JSONDecodeError:
        print("Error: AI response is not valid JSON.")
        return render_template("results.html", matches=[], query=query)

    return render_template("results.html", matches=ai_matches, query=query)

if __name__ == "__main__":
    app.run(debug=True)
