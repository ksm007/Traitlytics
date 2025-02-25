

from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
from joblib import Memory
import re

memory = Memory("/tmp/joblib_cache", verbose=0)


insights_template = """ You are a personality analyst. Use plain text only. Do not use bold, italics, bullet points, or any special formatting. Provide meaningful content for each section. If any information is missing, write "Not available". Do not guess or hallucinate.

Profile Summary: Write a short, tailored summary of the individual's DISC type, work style, and professional strengths.

DISC Personality Type: Select ONLY ONE of these DISC types based on the individual's strengths and behaviors. Make sure your description fits their traits:

Leader (D)  (Dominance): Bold, decisive, and goal-focused. Often takes charge and excels in fast-paced environments, driving progress with determination and energy.

Pioneer (Di) (Dominance/Influence) Energetic, persuasive, and visionary. Combines assertiveness with enthusiasm to propel ideas forward and inspire others.

Influencer (I)  (Influence): Outgoing, optimistic, and spontaneous, bringing energy and positivity to interactions. Builds a friendly, collaborative atmosphere and serves as a social connector. iD (Influence/Dominance): Extroverted and driven, pairing social charm with ambition to achieve results.

Supporter (IS) (Influence/Steadiness) Empathetic, approachable, and consistent, prioritizing collaboration and harmony within teams.

Supporter (S)  (Steadiness): Reliable, empathetic, and cooperative, valuing stability and supporting group cohesion. Si (Steadiness/Influence): Warm, service-oriented, and adept at encouraging collaboration and consensus.

Specialist (SC) (Steadiness/Conscientiousness): Detail-oriented, dependable, and analytical. Strongly favors systematic planning and thorough analysis, ensuring tasks are completed with precision and care. Their loyalty and thoughtful approach make them ideal for roles requiring meticulous planning and strict adherence to procedures. They excel in environments that prioritize accuracy and long-term reliability.

Specialist (CS) (Conscientiousness/Steadiness): Dependable and methodical, thriving in structured environments that emphasize clear procedures and stability.

Analyzer (C) (Conscientiousness) Precise, analytical, and dependable, emphasizing thorough research and high-quality results. Focuses on details and accuracy. 

Analyzer (CD) (Conscientiousness/Dominance): A blend of logical problem-solving and action-oriented drive, striving for measurable outcomes backed by careful analysis.

Strategist (DC) (Dominance/Conscientiousness) Direct, analytical, and efficient, with a goal-centered approach that values structure and logical methods.

Format your answer like this example: "DISC Personality Type: Leader – D (Dominance): Decisive, results-focused, and thrives in fast-paced environments, often taking charge and prioritizing outcomes over consensus."

Personality Diagram: 
Describe the individual’s DISC traits in one sentence using relevant traits given below: 
1. Dominance (D): Bold and results-driven. 
2. Influence (i): Outgoing and charismatic. 
3. Steadiness (S): Patient and dependable. 
4. Conscientiousness (C): Detail-oriented and logical.

Key Traits: Trait 1: Short description. Trait 2: Short description. Trait 3: Short description.

Do's: Provide two actionable suggestions that the interviewee can implement during the interview with this person to effectively showcase their strengths and personality.

Don'ts: Mention two behaviors or mistakes the interviewee should avoid during the interview with this person to maintain a positive impression.

 """



model = OllamaLLM(model="llama3.1:latest")
# @memory.cache
def generate_llm_insights(profile_data):
    if not profile_data:
        return "No data provided for generating insights."

    profile_data_str = "\n".join(
        f"{key.capitalize()}: {value.strip()}" for key, value in profile_data.items() if value and isinstance(value, str) 
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
        "Personality_Diagram": "",
        "Key_Traits": [],
        "Dos": [],
        "Donts": []
    }

    try:
        # Define regex patterns for each section
        section_patterns = {
            "DISC_Personality_Type": r"DISC Personality Type:([\s\S]*?)(?=Profile Summary:|Personality Diagram:|Key Traits:|Do's:|Don'ts:|$)",
            "Profile_Summary": r"Profile Summary:([\s\S]*?)(?=DISC Personality Type:|Personality Diagram:|Key Traits:|Do's:|Don'ts:|$)",
            "Personality_Diagram": r"Personality Diagram[\s:]*([\s\S]*?)(?=DISC Personality Type:|Profile Summary:|Key Traits:|Do's:|Don'ts:|$)",
            "Key_Traits": r"Key Traits:([\s\S]*?)(?=DISC Personality Type:|Profile Summary:|Personality Diagram:|Do's:|Don'ts:|$)",
            "Dos": r"Do's:([\s\S]*?)(?=DISC Personality Type:|Profile Summary:|Personality Diagram:|Key Traits:|Don'ts:|$)",
            "Donts": r"Don'ts:([\s\S]*?)(?=DISC Personality Type:|Profile Summary:|Personality Diagram:|Key Traits:|Do's:|$)"
        }

        # Extract each section using regex
        for key, pattern in section_patterns.items():
            match = re.search(pattern, cleaned_insights, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                # Split multiline content into a list for these sections
                if key in {"Key_Traits", "Dos", "Donts"}:
                    structured_response[key] = [
                        line.strip() for line in content.split("\n") if line.strip()
                    ]
                else:
                    structured_response[key] = content

        # Post-process for missing or malformed sections
        for key, value in structured_response.items():
            if not value:
                structured_response[key] = "Not available" if isinstance(value, str) else []

    except Exception as e:
        print(f"Error parsing insights: {e}")

    return structured_response
