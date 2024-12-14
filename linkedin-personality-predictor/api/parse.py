# from langchain_ollama import OllamaLLM
# from langchain.prompts import ChatPromptTemplate
# import json

# template = (
#     "You are tasked with extracting relevant information from a LinkedIn profile. "
#     "From the following content: {dom_content}, please extract the person's professional experiences, education, skills, endorsements, recommendations, and any other information that could be used to predict their personality type. "
#     "Your response should be a containing this information. Do not include any additional text or explanations."
# )

# model = OllamaLLM(model="llama3.1:latest")

# # def parse_with_ollama(content):
# #     # Properly escape template variables
# #     prompt = ChatPromptTemplate.from_template(template)
# #     chain = prompt | model

# #     # Invoke the chain and parse the response
# #     response = chain.invoke({"dom_content": content})

# #     # Log the raw response for debugging
# #     print("Raw response from LLM:", response)

# #     # Attempt to parse JSON
# #     try:
# #         response_json = json.loads(response)
# #     except json.JSONDecodeError:
# #         # Log the fallback situation
# #         print("Fallback: Response is not JSON.")
# #         response_json = {
# #             "name": response_json.get("name", "N/A"),
# #             "skills": response_json.get("skills", []),
# #             "error": "The model did not return a valid JSON. Raw response: " + response
# #         }

# #     # Add default values for any additional keys
# #     if 'name' not in response_json:
# #         response_json['name'] = "N/A"
# #     if 'professional_experiences' not in response_json:
# #         response_json['professional_experiences'] = []

# #     return response_json
# def parse_with_ollama(content):
#     # Properly escape template variables
#     prompt = ChatPromptTemplate.from_template(template)
#     chain = prompt | model

#     # Invoke the chain and parse the response
#     response = chain.invoke({"dom_content": content})

#     # # Attempt to parse JSON and handle errors
#     # try:
#     #     response_json = json.loads(response)
#     # except json.JSONDecodeError:
#     #     # Handle cases where the model output is not valid JSON
#     #     response_json = {
#     #         "name": "N/A",
#     #         "skills": [],
#     #         "error": "Invalid JSON: " + response
#     #     }
#     #     return {
#     #     "Name": response_json.get("name", "N/A"),
#     #     "Skills": response_json.get("skills", []),
#     #     "Professional Experiences": response_json.get("professional_experiences", []),
#     #     "Error": response_json.get("error", None)
#     # }

#     # # Simplify the output for better readability
#     # parsed_data = {
#     #     "Name": response_json.get("name", "N/A"),
#     #     "Skills": response_json.get("skills", []),
#     #     "Professional Experiences": response_json.get("professional_experiences", []),
#     #     "Error": response_json.get("error", None)
#     # }

#     try:
#         parsed_data = {
#         "Name": "Sample Name",  # Extracted from content
#         "Skills": ["Skill1", "Skill2"],
#         "Professional Experiences": [{"Company": "Company1", "Role": "Role1"}],
#         "Error": None
#             }
#     except Exception as e:
#         parsed_data = {
#             "Name": "N/A",
#             "Skills": [],
#             "Professional Experiences": [],
#             "Error": str(e)
#         }

#     # Return formatted output without raw JSON logging
#     return parsed_data