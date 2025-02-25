import requests
import logging
from joblib import Memory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up joblib caching
memory = Memory("/tmp/joblib_cache", verbose=0)

# Hugging Face API details
# API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-8B-Instruct"
API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"

HEADERS = {"Authorization": "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"}  # Replace with your actual API key


def query_llama_api(prompt):

    try:
        logger.info("Querying Hugging Face Inference API...")
        payload = {"inputs": prompt, "parameters": {"max_length": 1000, "temperature": 0.7}}
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()  # Raise HTTPError for bad responses

        # Parse response
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        else:
            logger.error("Unexpected response format")
            return "Unexpected response format. No 'generated_text' found."
    except Exception as e:
        logger.error(f"Error querying Hugging Face API: {e}")
        return f"Error: {e}"


@memory.cache
def generate_llm_insights(profile_data):

    if not profile_data:
        return "No data provided for generating insights."

    # Format the input profile data
    if isinstance(profile_data, dict):
        profile_data_str = "\n".join(f"{k}: {v}" for k, v in profile_data.items())
    else:
        profile_data_str = str(profile_data)

    # Define prompt template
    prompt = (
        "You are a skilled personality analyst using the DISC framework to evaluate professional profiles. "
        "Analyze the provided profile data: {data} and identify the individual's DISC personality type "
        "(D - Dominance, I - Influence, S - Steadiness, C - Conscientiousness). "
        "Provide actionable insights for interacting with this individual in professional settings.\n\n"
        "**Profile Summary**: Provide a concise overview of their personality.\n"
        "**DISC Personality Type**: Predict one DISC type (D/I/S/C) and explain why.\n"
        "**Key Traits**: List 3-5 defining traits.\n"
        "**Personality Diagram**: Describe visually (Leader, Promoter, Analyzer, Stabilizer).\n"
        "**Do's and Don'ts for Interaction**:\n"
        "- **Do**: Suggest 2 ways to interact effectively.\n"
        "- **Don't**: List 2 pitfalls to avoid."
    ).format(data=profile_data_str)

    logger.info("Sending formatted prompt to the LLaMA API...")
    response = query_llama_api(prompt)
    return response



# def generate_llm_insights(profile_data):
#     if not profile_data:
#         return "No data provided for generating insights."

#     # Clean the profile_data to ensure all values are strings
#     profile_data = {key: (value if value else "Not provided") for key, value in profile_data.items()}

#     # Prepare the input prompt
#     profile_data_str = "\n".join(
#         f"{key.capitalize()}: {value}" for key, value in profile_data.items()
#     )
#     prompt = f"""You are a skilled personality analyst using the DISC framework to evaluate professional profiles.
#     Analyze the provided profile data: {profile_data_str} and identify the individual's DISC personality type 
#     (D - Dominance, I - Influence, S - Steadiness, C - Conscientiousness).
#     Provide actionable insights for interacting with this individual in professional settings. Format your response as follows:

#     **Profile Summary:**
#     Provide a concise overview of the individual's personality based on their professional experiences, education, and skills.

#     **DISC Personality Type:**
#     Predict the primary DISC personality type. Include one type only (D, I, S, or C) and explain why this type applies based on the profile data.

#     **Key Traits:**
#     List three to five key traits that define this individual's behavior or work style.

#     **Personality Diagram:**
#     Describe their DISC type visually (e.g., Analyzer (C), Promoter (I), Stabilizer (S), Leader (D)).

#     **Do's and Don'ts for Interaction:**
#     - **Do:** Provide two actionable suggestions for effectively working with this individual.
#     - **Don't:** Provide two potential pitfalls to avoid when interacting with them."""

#     # API payload
#     payload = {"inputs": prompt, "parameters": {"max_length": 1024, "temperature": 0.7}}

#     try:
#         print(f"Sending request to Hugging Face API with prompt:\n{prompt}\n")
#         response = requests.post(API_URL, headers=headers, json=payload)
#         response.raise_for_status()  # Raise exception for HTTP errors

#         # Process response
#         result = response.json()
#         if "error" in result:
#             return f"Error: {result['error']}"
#         elif isinstance(result, list) and result:
#             return result[0].get("generated_text", "No insights found.")
#         else:
#             return "Unexpected API response format."
#     except requests.exceptions.HTTPError as http_err:
#         return f"HTTP error occurred: {http_err}"
#     except Exception as e:
#         return f"Error: {e}"

# @memory.cache
# def generate_llm_insights(profile_data):
#     if not profile_data:
#         return "No data provided for generating insights."

#     # Prepare the input prompt
#     profile_data_str = "\n".join(
#         f"{key.capitalize()}: {value}" for key, value in profile_data.items() if value
#     )
#     prompt = ("You are a skilled personality analyst using the DISC framework to evaluate professional profiles. "
#     "Analyze the provided profile data: {data} and identify the individual's DISC personality type (D - Dominance, I - Influence, S - Steadiness, C - Conscientiousness). "
#     "Provide actionable insights for interacting with this individual in professional settings. Format your response as follows:"

#     "\n\n**Profile Summary**:"
#     "\nProvide a concise overview of the individual's personality based on their professional experiences, education, and skills."

#     "\n\n**DISC Personality Type**:"
#     "\nPredict the primary DISC personality type. Include one type only (D, I, S, or C) and explain why this type applies based on the profile data."

#     "\n\n**Key Traits**:"
#     "\nList three to five key traits that define this individual's behavior or work style."

#     "\n\n**Personality Diagram**:"
#     "\nDescribe their DISC type visually (e.g., Analyzer (C), Promoter (I), Stabilizer (S), Leader (D))."

#     "\n\n**Do's and Don'ts for Interaction**:"
#     "\n- **Do:** Provide two actionable suggestions for effectively working with this individual."
#     "\n- **Don't:** Provide two potential pitfalls to avoid when interacting with them.").format(data=profile_data_str)

#     # Make the API request
#     payload = {"inputs": prompt, "parameters": {"max_length": 1024, "temperature": 0.7}}
#     try:
#         response = requests.post(API_URL, headers=HEADERS, json=payload)
#         response.raise_for_status()  # Raise exception for HTTP errors
#         result = response.json()

#         # Extract the generated text from the response
#         if isinstance(result, dict) and "error" in result:
#             return f"Error: {result['error']}"
#         elif isinstance(result, list) and "insights" in result[0]:
#             return result[0]["insights"]
#         else:
#             return "Unexpected API response format."
#     except Exception as e:
#         print(f"Error generating insights: {e}")
#         return f"Error: {e}"

