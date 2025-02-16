from flask import Flask, request, jsonify
from scrape import scrape_website
from llm_insights import generate_llm_insights,parse_llm_response
from flask_cors import CORS
import re
app = Flask(__name__)
CORS(app)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    website_url = data.get("url")

    if not website_url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # Step 1: Scrape profile data
        profile_data = scrape_website(website_url)
        print("Data Extraction complete")
        print(f"Profile Data: {profile_data}")

        if not profile_data or not any(profile_data.values()):
            return jsonify({"error": "Failed to scrape content or insufficient data from the provided URL."}), 400


        # Step 2: Generate LLM insights
        insights = generate_llm_insights(profile_data)
        print("------------------------ ------------------------ ------------------------ ------------------------")
        
        # Step 3: Parse structured sections from insights
        cleaned_insights = clean_markdown(insights)
        structured_response = parse_llm_response(cleaned_insights)
        print(f"Generated Insights: {structured_response}")

        # Step 4: Return structured JSON response
        return jsonify(structured_response), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

def clean_markdown(text):
    """
    Remove Markdown-style bold (**text**) and clean unnecessary whitespace.
    """
    cleaned_text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # Remove bold formatting
    cleaned_text = re.sub(r"\n{2,}", "\n", cleaned_text).strip()  # Remove extra newlines
    cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text)  # Remove extra spaces
    return cleaned_text


if __name__ == "__main__":
    app.run(debug=True, port=5000)
