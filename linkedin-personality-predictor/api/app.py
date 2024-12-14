from flask import Flask, request, jsonify
from scrape import scrape_website, extract_body_content, clean_body_content
# from parse import parse_with_ollama
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
        url = request.json['url']
        raw_html = scrape_website(url)
        print(f"Raw HTML:{raw_html} ")


        if not raw_html.strip():
            return jsonify({"error": "Failed to scrape content from the provided URL."}), 400

        insights = generate_llm_insights(raw_html)
        print(f"insights{insights}")
        return jsonify({"insights": insights})

    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    app.run(debug=True, port=5000)



# from flask import Flask, request, jsonify
# from scrape import scrape_website, extract_profile_data
# from llm_insights import generate_llm_insights
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)

# @app.route('/scrape', methods=['POST'])
# def scrape():
#     data = request.json
#     website_url = data.get("url")

#     if not website_url:
#         return jsonify({"error": "URL is required"}), 400

#     try:
#         raw_html = scrape_website(website_url)

#         if not raw_html.strip():
#             return jsonify({"error": "Failed to scrape content from the provided URL."}), 400

#         # Optionally extract profile data for structured output
#         driver = None  # Pass your driver instance if needed
#         profile_data = extract_profile_data(driver, website_url)

#         # Print profile data to console for debugging
#         print("Extracted Profile Data:", profile_data)

#         insights = generate_llm_insights(profile_data)
        
#         return jsonify({"insights": insights, "profile_data": profile_data})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)
