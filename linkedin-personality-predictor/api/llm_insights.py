from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
import json
from joblib import Memory

memory = Memory("/tmp/joblib_cache", verbose=0)


# ''')
# insights_template = (
#     "You are an insightful personality analyst skilled in evaluating LinkedIn profiles. "
#     "Review the provided profile data and generate actionable insights using the DISC personality framework. "
#     "Structure your response as follows:"
#     "\n\nProfile Data:\n{data}"
#     "\n\nOutput Format:"
#     "\n**Personality Type**: Provide the primary DISC personality type (e.g., Analyzer (C)) and a one-line summary."
#     "\n**Personality Description**: Give a detailed explanation of the personality type, highlighting work habits, strengths, and behaviors."
#     "\n**Do's and Don'ts for Interaction**:"
#     "\n    - **Do:** Provide two specific actions or approaches to interact effectively with this individual."
#     "\n    - **Don't:** Provide two specific actions or behaviors to avoid during interactions."
# )

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

def compute_reward(response_text, user_feedback=None):
    """
    Compute a reward score based on the presence of desired elements in the response.
    Adjust the reward based on user feedback.
    """
    # Define keywords or phrases that are important
    desired_elements = [
        "profile summary", "identify disc personality type", "keywords and indicators",
        "strengths", "areas for development", "recommendations", "adaptability"
    ]
    base_reward = sum(1 for element in desired_elements if element in response_text.lower())

    # Adjust reward based on user feedback
    if user_feedback == 'positive':
        reward = base_reward + 5  # Boost reward if user liked the insight
    elif user_feedback == 'negative':
        reward = base_reward - 5  # Penalize if user didn't like the insight
    else:
        reward = base_reward  # No adjustment if no feedback

    return reward

@memory.cache
def generate_llm_insights(parsed_results, user_feedback=None):
    # Ensure parsed_results is properly formatted
    if isinstance(parsed_results, dict):
        # Convert dict to a plain text representation
        data_lines = []
        for key, value in parsed_results.items():
            data_lines.append(f"{key}: {value}")
        data_representation = '\n'.join(data_lines)
    elif isinstance(parsed_results, str):
        data_representation = parsed_results
    else:
        raise ValueError("Unsupported data type in parsed_results.")

    # Initialize variables for RL loop
    max_iterations = 3  # Number of iterations for refinement
    best_response = None
    best_reward = -float('inf')

    for iteration in range(max_iterations):
        # Create the prompt template
        prompt_template = ChatPromptTemplate.from_template(insights_template)
        chain = prompt_template | model

        # Generate the insights by invoking the chain with the input data
        response = chain.invoke({
            "data": data_representation,
        })

        # Compute the reward
        reward = compute_reward(response, user_feedback)

        print(f"Iteration {iteration+1}: Reward = {reward}")

        # If this response is better, update best_response
        if reward > best_reward:
            best_reward = reward
            best_response = response

        # If user provided negative feedback, modify the prompt (simulating policy update)
        if user_feedback == 'negative':
            # Adjust the prompt to emphasize adherence to guidelines
            insights_template_modified = insights_template + "\nPlease ensure your analysis strictly follows the guidelines above and addresses the user's needs."
            prompt_template = ChatPromptTemplate.from_template(insights_template_modified)
            chain = prompt_template | model

    print("Generated insights for the provided data")
    return best_response