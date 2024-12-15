from flask import Flask, request, jsonify
from scrape import scrape_website
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
        profile_data = scrape_website(website_url)  # Get structured profile data
        print("Data extraction complete")
        print(f"Profile Data: {profile_data}")

        if not profile_data:
            return jsonify({"error": "Failed to scrape content from the provided URL."}), 400

        insights = generate_llm_insights(profile_data)
        print(f"Insights: {insights}")
        return jsonify({"insights": insights})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
