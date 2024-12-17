
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
from joblib import Memory
import re

memory = Memory("/tmp/joblib_cache", verbose=0)



# insights_template = (
#     "You are a skilled personality analyst utilizing the DISC framework to evaluate professional profiles. "
#     "Your task is to analyze the provided profile data (including professional experiences, education, and skills) and determine the individual's DISC personality type. "
#     "The DISC types include primary types (D - Dominance, I - Influence, S - Steadiness, C - Conscientiousness) and their combinations (e.g., DC, CD, SC). Select **only one** personality type (primary or combination)."

#     "\n\n**Instructions:**"
#     "\n1. Review the provided profile data: {data}."
#     "\n2. Identify and select the single best DISC personality type that fits the individual."
#     "\n3. Provide a descriptor (e.g., Analyzer (C), Leader (CD), Supporter (SC)) with a clear explanation of their type."
#     "\n4. Offer actionable insights for interacting with this individual."

#     "\n\nFormat your response as follows:"

#     "\n\nDISC Personality Type:"
#     "\nState the single DISC personality type (primary or combination) and describe it. For example: **Analyzer (C)**, **Leader (CD)**, or **Supporter (SC)**."

#     "\n\nProfile Summary:"
#     "\nProvide a concise, structured overview of the individual's personality, focusing on their professional experiences, work style, and key attributes."

#     "\n\nKey Traits:"
#     "\nList three to five defining traits that characterize this individual's behavior or approach to work."

#     "\n\nExplanation:"
#     "\nProvide a brief, clear explanation of why the chosen DISC personality type applies to the individual, backed by specific details from the profile data."
# )

insights_template = """
You are a DISC personality analyst. Follow this format exactly and use plain text only. DO NOT use bold, italics, bullet points, or any special formatting. Ensure each section has meaningful content. If data is unavailable, write 'Not available'.

DISC Personality Type:
Primary DISC type here 

Profile Summary:
Short summary here (1-2 sentences) about the individual's DISC type, skills, and work style.

Key Traits:
1. Trait 1: Short description
2. Trait 2: Short description
3. Trait 3: Short description

Personality Diagram :
When describing this diagram in your prompt to generate text for a class, you can say:

"This diagram represents the DISC Personality Model, dividing individuals into four main personality types: Dominance (D), Influence (i), Steadiness (S), and Conscientiousness (C). Each quadrant includes specific personality subtypes:

D: Goal-oriented and decisive.
i: Enthusiastic and persuasive.
S: Supportive and patient.
C: Analytical and detail-focused.
Please generate a description for the [INSERT PERSONALITY CLASS, e.g., Conscientiousness (C)], including its traits, strengths, weaknesses, and ideal work environments."

Do's:
1. Provide one actionable suggestion for effectively working with this individual.
2. Provide another actionable suggestion for effectively working with this individual.

Don'ts:
1. Mention one potential pitfall to avoid when interacting with this individual.
2. Mention another potential pitfall to avoid when interacting with this individual.
"""






model = OllamaLLM(model="llama3.1:latest")
@memory.cache
def generate_llm_insights(profile_data):
    if not profile_data:
        return "No data provided for generating insights."

    # Convert profile_data dictionary into a readable string for the LLM
    profile_data_str = "\n".join(
        f"{key.capitalize()}: {value}" for key, value in profile_data.items() if value
    )

    prompt_template = ChatPromptTemplate.from_template("{insights_template}\n\n{data}")
    chain = prompt_template | model

    # Generate insights with correct placeholders
    response = chain.invoke({
        "insights_template": insights_template,
        "data": profile_data_str,
    })

 

    print("Generated insights for the provided profile data")
    return response

def parse_llm_response(cleaned_insights):
    structured_response = {
        "DISC_Personality_Type": "",
        "Profile_Summary": "",
        "Key_Traits": [],
        "Personality_Diagram": "",
        "Dos": [],
        "Donts": []
    }

    try:
        lines = cleaned_insights.split("\n")
        current_section = None

        for line in lines:
            line = line.strip()

            if "DISC Personality Type:" in line:
                current_section = "DISC_Personality_Type"
                structured_response[current_section] = line.split(":", 1)[1].strip()
            elif "Profile Summary:" in line:
                current_section = "Profile_Summary"
                structured_response[current_section] = ""
            elif "Key Traits:" in line:
                current_section = "Key_Traits"
                structured_response[current_section] = []
            elif "Personality Diagram:" in line:
                current_section = "Personality_Diagram"
                structured_response[current_section] = ""
            elif "Do's:" in line:
                current_section = "Dos"
                structured_response[current_section] = []
            elif "Don'ts:" in line:
                current_section = "Donts"
                structured_response[current_section] = []
            elif current_section:
                if isinstance(structured_response[current_section], list):
                    structured_response[current_section].append(line)
                else:
                    structured_response[current_section] += f" {line}".strip()
    except Exception as e:
        print(f"Error parsing insights: {e}")
    return structured_response
