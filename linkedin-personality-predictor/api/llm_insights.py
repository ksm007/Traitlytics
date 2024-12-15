
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
from joblib import Memory

memory = Memory("/tmp/joblib_cache", verbose=0)

# insights_template = (
#     "You are a skilled personality analyst using the DISC framework to evaluate professional profiles. "
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
#     "\n- **Don't:** Provide two potential pitfalls to avoid when interacting with them."
# )

insights_template = (
    "You are a skilled personality analyst utilizing the DISC framework to evaluate professional profiles. "
    "Your task is to analyze the provided profile data (including professional experiences, education, and skills) and determine the individual's DISC personality type. "
    "The DISC types include primary types (D - Dominance, I - Influence, S - Steadiness, C - Conscientiousness) and their combinations (e.g., DC, CD, SC). Select **only one** personality type (primary or combination)."

    "\n\n**Instructions:**"
    "\n1. Review the provided profile data: {data}."
    "\n2. Identify and select the single best DISC personality type that fits the individual."
    "\n3. Provide a descriptor (e.g., Analyzer (C), Leader (CD), Supporter (SC)) with a clear explanation of their type."
    "\n4. Offer actionable insights for interacting with this individual."

    "\n\nFormat your response as follows:"

    "\n\n**DISC Personality Type:**"
    "\nState the single DISC personality type (primary or combination) and describe it. For example: **Analyzer (C)**, **Leader (CD)**, or **Supporter (SC)**."

    "\n\n**Profile Summary:**"
    "\nProvide a concise, structured overview of the individual's personality, focusing on their professional experiences, work style, and key attributes."

    "\n\n**Key Traits:**"
    "\nList three to five defining traits that characterize this individual's behavior or approach to work."

    "\n\n**Explanation:**"
    "\nProvide a brief, clear explanation of why the chosen DISC personality type applies to the individual, backed by specific details from the profile data."
)



model = OllamaLLM(model="llama3.1:latest")
@memory.cache
def generate_llm_insights(profile_data):
    if not profile_data:
        return "No data provided for generating insights."

    # Convert profile_data dictionary into a readable string for the LLM
    profile_data_str = "\n".join(
        f"{key.capitalize()}: {value}" for key, value in profile_data.items() if value
    )

    # Create the prompt template
    prompt_template = ChatPromptTemplate.from_template(insights_template)
    chain = prompt_template | model

    # Generate the insights by invoking the chain with the input data
    response = chain.invoke({
        "data": profile_data_str,  
    })

    print("Generated insights for the provided profile data")
    return response

