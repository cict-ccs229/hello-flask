from flask import Flask, jsonify, render_template, request
import json

app = Flask(__name__)

# Load the diseases data from the JSON file
def load_diseases():
    with open('diseases.json', 'r') as file:
        return json.load(file)

# Home endpoint that shows the index.html page with pagination
@app.route('/')
def home():
    diseases = load_diseases()
    page = request.args.get('page', 1, type=int)  # Get current page, default is 1
    start = (page - 1) * 10
    end = start + 10
    diseases_to_show = diseases[start:end]
    
    # Calculate the total number of pages
    total_pages = (len(diseases) // 10) + (1 if len(diseases) % 10 > 0 else 0)
    
    # Generate page numbers for navigation with ellipses
    page_numbers = []
    if total_pages <= 10:
        page_numbers = list(range(1, total_pages + 1))
    else:
        if page <= 5:
            page_numbers = list(range(1, 6)) + ['...'] + [total_pages]
        elif page >= total_pages - 4:
            page_numbers = [1] + ['...'] + list(range(total_pages - 4, total_pages + 1))
        else:
            page_numbers = [1] + ['...'] + list(range(page - 2, page + 3)) + ['...'] + [total_pages]

    return render_template('index.html', diseases=diseases_to_show, page=page, total_pages=total_pages, page_numbers=page_numbers)

# Endpoint to search for diseases based on query keyword
@app.route('/search', methods=['GET'])
def search_diseases():
    query = request.args.get('query', '').lower()  # Get the query from the form
    diseases = load_diseases()
    
    # Filter diseases by matching the query with disease name or synonyms
    matching_diseases = [
        disease for disease in diseases if query in disease['primary_name'].lower() or query in disease['word_synonyms'].lower()
    ]
    
    page = request.args.get('page', 1, type=int)  # Get current page, default is 1
    start = (page - 1) * 10
    end = start + 10
    diseases_to_show = matching_diseases[start:end]
    
    # Calculate the total number of pages
    total_pages = (len(matching_diseases) // 10) + (1 if len(matching_diseases) % 10 > 0 else 0)
    
    # Generate page numbers for navigation with ellipses
    page_numbers = []
    if total_pages <= 10:
        page_numbers = list(range(1, total_pages + 1))
    else:
        if page <= 5:
            page_numbers = list(range(1, 6)) + ['...'] + [total_pages]
        elif page >= total_pages - 4:
            page_numbers = [1] + ['...'] + list(range(total_pages - 4, total_pages + 1))
        else:
            page_numbers = [1] + ['...'] + list(range(page - 2, page + 3)) + ['...'] + [total_pages]
    
    return render_template('index.html', diseases=diseases_to_show, page=page, total_pages=total_pages, page_numbers=page_numbers, query=query)

# Endpoint to get details about a specific disease by key_id
@app.route('/disease/<string:key_id>', methods=['GET'])
def get_disease_info(key_id):
    diseases = load_diseases()
    disease = next((d for d in diseases if d["key_id"] == key_id), None)
    
    if disease is None:
        return jsonify({"message": "Disease not found"}), 404
    
    return render_template('diseases.html', disease=disease)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
