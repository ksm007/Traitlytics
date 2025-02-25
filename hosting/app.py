from flask import Flask, request, jsonify
from scrape import scrape_website
# from llm_insights import generate_llm_insights
from flask_cors import CORS
import requests

app = Flask(__name__)




CORS(app)

# HUGGINGFACE_API_URL = "https://kuntal01-meta-llama-Llama-3.1-8B.hf.space/run/predict"
# def call_huggingface_api(profile_data):
#     """Send profile data to Hugging Face API."""
#     try:
#         # Unpack profile_data into separate values
#         headline = profile_data.get("headline", "Not provided")
#         about = profile_data.get("about", "Not provided")
#         education = profile_data.get("education", "Not provided")
#         experience = profile_data.get("experience", "Not provided")

#         response = requests.post(
#             HUGGINGFACE_API_URL,
#             json={"data": [headline, about, education, experience]}  # Send as list
#         )
#         response.raise_for_status()
#         result = response.json()
#         return result.get("data", ["No insights returned."])[0]  # Extract the first response
#     except Exception as e:
#         return f"Error calling Hugging Face API: {str(e)}"




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

        
        # Clean the profile_data to handle None values
        profile_data = {key: (value if value else "Not provided") for key, value in profile_data.items()}

        # insights = generate_llm_insights(profile_data)
        insights = call_huggingface_api(profile_data)

        print(f"Insights: {insights}")
        return jsonify({"insights": insights})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)

