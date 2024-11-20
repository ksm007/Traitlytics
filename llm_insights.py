from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
import json
from joblib import Memory

memory = Memory("/tmp/joblib_cache", verbose=0)

# insights_template = ('''
# You are an insightful personality analyst skilled in evaluating LinkedIn profiles. Review the provided profile data, focusing on keywords, role descriptions, and language use, to predict the individual's personality type, similar to the DISC framework.

# Profile Data:
# {data}

# Please follow these general guidelines:
# 1. **Profile Summary**: Provide a concise overview that highlights key personality traits based on the profile's keywords and tone of communication.

# 2. **Identify DISC Personality Type**: Predict the personality type (D - Dominance, I - Influence, S - Steadiness, C - Conscientiousness) based on observed traits. For example:
#    - **D (Dominance)**: Results-oriented, decisive, direct, and takes charge.
#    - **I (Influence)**: People-focused, persuasive, enthusiastic, and social.
#    - **S (Steadiness)**: Dependable, calm, supportive, and reliable.
#    - **C (Conscientiousness)**: Detail-oriented, analytical, cautious, and thorough.

# 3. **Keywords and Indicators**: List specific keywords or phrases in the profile that led to the personality prediction.

# 4. **Relevant Strengths and Potential Areas for Development**: Based on the personality prediction, outline strengths relevant to various professional contexts (e.g., team leadership, client relations, technical roles) and areas where the individual might benefit from development.

# 5. **Generalized Recommendations**: Offer advice on potential career paths, roles, or work environments that align with the predicted personality type.

# 6. **Cross-Context Adaptability**: Present findings in a way that could be useful across multiple industries, making insights universally relevant.
# ''')

insights_template = (
    "You are an insightful personality analyst skilled in evaluating LinkedIn profiles. "
    "Review the provided profile data, focusing on keywords, role descriptions, and language use, to predict the individual's personality type, similar to the DISC framework. "
    "\n\nProfile Data:\n{data}"
    "\n\nPlease follow these general guidelines:"
    "\n1. **Profile Summary**: Provide a concise overview that highlights key personality traits based on the profile's keywords and tone of communication."
    "\n2. **Identify DISC Personality Type**: Predict the personality type (D - Dominance, I - Influence, S - Steadiness, C - Conscientiousness) based on observed traits."
    "\n3. **Keywords and Indicators**: List specific keywords or phrases in the profile that led to the personality prediction."
    "\n4. **Relevant Strengths and Potential Areas for Development**: Based on the personality prediction, outline strengths and areas for improvement."
    "\n5. **Generalized Recommendations**: Suggest potential career paths or roles that align with the predicted personality type."
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