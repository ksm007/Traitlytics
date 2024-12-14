
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
from joblib import Memory

memory = Memory("/tmp/joblib_cache", verbose=0)

insights_template = (
    "You are a skilled personality analyst using the DISC framework to evaluate professional profiles. "
    "Analyze the provided profile data: {data} and identify the individual's DISC personality type (D - Dominance, I - Influence, S - Steadiness, C - Conscientiousness). "
    "Provide actionable insights for interacting with this individual in professional settings. Format your response as follows:"

    "\n\n**Profile Summary**:"
    "\nProvide a concise overview of the individual's personality based on their professional experiences, education, and skills."

    "\n\n**DISC Personality Type**:"
    "\nPredict the primary DISC personality type. Include one type only (D, I, S, or C) and explain why this type applies based on the profile data."

    "\n\n**Key Traits**:"
    "\nList three to five key traits that define this individual's behavior or work style."

    "\n\n**Personality Diagram**:"
    "\nDescribe their DISC type visually (e.g., Analyzer (C), Promoter (I), Stabilizer (S), Leader (D))."

    "\n\n**Do's and Don'ts for Interaction**:"
    "\n- **Do:** Provide two actionable suggestions for effectively working with this individual."
    "\n- **Don't:** Provide two potential pitfalls to avoid when interacting with them."
)

model = OllamaLLM(model="llama3.1:latest")
# @memory.cache
def generate_llm_insights(raw_data):
    if not raw_data:
        return "No data provided for generating insights."

    # Create the prompt template
    prompt_template = ChatPromptTemplate.from_template(insights_template)
    chain = prompt_template | model

    # Generate the insights by invoking the chain with the input data
    response = chain.invoke({
        "data": raw_data,
    })

    print("Generated insights for the provided data")
    return response


# @memory.cache
# def generate_llm_insights(profile_data):
#     if not profile_data:
#         return "No profile data provided for generating insights."

#     # Modify the prompt to use structured profile data
#     response = chain.invoke({
#         "data": profile_data,
#     })

#     print("Generated insights for the provided data")
#     return response

