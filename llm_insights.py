from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
import json
from joblib import Memory

memory = Memory("/tmp/joblib_cache", verbose=0)

insights_template = (

    "You are an insightful personality analyst skilled in evaluating LinkedIn profiles. "
    "Review the provided profile data, focusing on keywords, role descriptions, and language use, to predict the individual's personality type, similar to the DISC framework. "
    "\n\nProfile Data:\n{dom_content}"
    "\n\nPlease follow these general guidelines:"
    "\n1. **Profile Summary**: Provide a concise overview that highlights key personality traits based on the profile's keywords and tone of communication."
    "\n2. **Identify DISC Personality Type**: Predict the personality type (D - Dominance, I - Influence, S - Steadiness, C - Conscientiousness) based on observed traits."
    "\n3. **Keywords and Indicators**: List specific keywords or phrases in the profile that led to the personality prediction."
    "\n4. **Do's and Don'ts for Interviews:**"
    "\n    - **Do:** Provide two actionable suggestions for effectively collaborating with or working alongside this individual."
    "\n    - **Don't:** Highlight two potential pitfalls to avoid when interacting or interviewing with this person."
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
@memory.cache
def generate_llm_insights(dom_content, user_feedback=None):
    """
    Generate personality insights directly from DOM content.
    """
    # Check if DOM content is empty
    if not dom_content or not isinstance(dom_content, str) or dom_content.strip() == "":
        return "Data not found. Please ensure the LinkedIn profile URL is valid and accessible."

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
            "dom_content": dom_content,
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
