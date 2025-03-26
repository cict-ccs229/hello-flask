import json
from flask import Flask, request, render_template

app = Flask(__name__)

# Load diseases data from JSON file
with open('diseases.json', 'r') as file:
    diseases = json.load(file)

@app.route('/')
def index():
    query = request.args.get('query', '')
    results = []

    if query:
        query_lower = query.lower()
        for disease in diseases:
            if any(query_lower in str(value).lower() for value in disease.values()):
                results.append(disease)

    return render_template('index.html', query=query, results=results)

if __name__ == '__main__':
    app.run(debug=True)
