# Albularyo Web Application

## Overview

Albularyo is a web application designed to help users diagnose potential diseases based on their symptoms. The application provides a user-friendly interface where users can select symptoms and receive possible diagnoses. Additionally, the application features an AI chatbot that uses the Gemini API to dynamically respond to user queries based on the diseases data.

## Features

1. **Symptom-Based Diagnosis**:
    - Users can select symptoms from a predefined list or enter additional symptoms manually.
    - The application matches the provided symptoms with a list of diseases and returns possible diagnoses.
    - Each diagnosis includes the disease name, ICD code, and a link to more information if available.

2. **AI Chatbot**:
    - The application includes a chatbot interface where users can interact with an AI assistant.
    - The chatbot uses the Gemini API to dynamically utilize the diseases JSON file and respond to user queries.
    - The chatbot can provide information about diseases, symptoms, and other medical-related queries.

## Usage

### Home Page

1. **Select Symptoms**:
    - On the home page, users can select symptoms from a list of checkboxes.
    - Users can also enter additional symptoms in the "Other Symptoms" input field.

2. **Submit Symptoms**:
    - After selecting symptoms, users can click the "Submit" button to receive possible diagnoses.
    - The results will be displayed below the form, showing the disease name, ICD code, and a link to more information if available.

3. **Chat with AI**:
    - Users can click the "Chat" button to navigate to the chatbot interface.

### Chatbot Page

1. **Interact with AI**:
    - On the chatbot page, users can enter their queries in the input field and receive responses from the AI assistant.
    - The AI uses the Gemini API to dynamically reference the diseases JSON file and provide accurate responses based on the user's input.

## Installation

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/yourusername/albularyo.git
    cd albularyo
    ```

2. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Set Up Environment Variables**:
    - Create a `.env` file in the root directory and add your Gemini API key:
    ```
    GEMINI_API_KEY=your_gemini_api_key
    ```

4. **Run the Application**:
    ```sh
    flask run
    ```

## File Structure

- `app.py`: Main application file that handles routes and logic for symptom-based diagnosis.
- `chat.py`: Blueprint for the chatbot functionality, including routes and logic for interacting with the Gemini API.
- `templates/`: Directory containing HTML templates for the web pages.
  - `index.html`: Home page template.
  - `chat.html`: Chatbot page template.
- `static/`: Directory containing static files such as CSS and JavaScript.
- `diseases.json`: JSON file containing the list of diseases and their attributes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Flask: Micro web framework for Python.
- Gemini API: Used for AI chatbot functionality.
- Bootstrap: CSS framework for responsive design.