from flask import Flask, request, jsonify
from scrape import scrape_website, extract_body_content, clean_body_content
from parse import parse_with_ollama
from llm_insights import generate_llm_insights
from flask_cors import CORS
app = Flask(__name__)


CORS(app)


@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    website_url = data.get("url")

    if not website_url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # Log each step
        print("Scraping website...")
        raw_html = scrape_website(website_url)
        print(f"Raw HTML: {raw_html[:500]}")

        body_content = extract_body_content(raw_html)
        print(f"Body Content: {body_content[:500]}")

        cleaned_content = clean_body_content(body_content)
        print(f"Cleaned Content: {cleaned_content[:500]}")

        parsed_result = parse_with_ollama(cleaned_content)
        print(f"Parsed Result: {parsed_result}")

        insights = generate_llm_insights(parsed_result)
        print(f"Insights: {insights}")

        return jsonify({"insights": insights})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
