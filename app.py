import base64
from io import BytesIO

import streamlit as st
from PIL import Image

from scrape import scrape_website, extract_body_content, clean_body_content
from parse import parse_with_ollama
from llm_insights import generate_llm_insights



# Set up Streamlit page configuration
st.set_page_config(page_title="LinkedIn Personality Predictor",  layout="wide")



# Header and title styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 3rem;
        color: #ff6347;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
        text-shadow: 3px 3px 2px #FFFF;
    }
    .sub-title {
        font-size: 1.5rem;
        color: #4f8a8b;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True
)

st.markdown("<h1 class='main-title'>LinkedIn Personality Predictor</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='sub-title'>Discover personality insights from LinkedIn profiles.</p>",
    unsafe_allow_html=True
)

# Input for LinkedIn profile URL
linkedin_url = st.text_input("Enter the LinkedIn Profile URL")

# Initialize session state variables
if 'dom_content' not in st.session_state:
    st.session_state.dom_content = ''
if 'parsed_result' not in st.session_state:
    st.session_state.parsed_result = ''
if 'generated_insights' not in st.session_state:
    st.session_state.generated_insights = ''
if 'user_feedback' not in st.session_state:
    st.session_state.user_feedback = None

# Scrape the LinkedIn profile when the button is clicked
if st.button("Scrape LinkedIn Profile"):
    if linkedin_url:
        st.write(f"Scraping {linkedin_url}...")
        try:
            dom_content = scrape_website(linkedin_url)
            if dom_content is None:
                st.error(f"Failed to scrape the LinkedIn profile: {linkedin_url}")
            else:
                body_content = extract_body_content(dom_content)
                cleaned_content = clean_body_content(body_content)
                st.session_state.dom_content = cleaned_content
        except Exception as e:
            st.error(f"Error scraping LinkedIn profile {linkedin_url}: {str(e)}")
    else:
        st.error("Please enter a LinkedIn profile URL.")

# Parse the content and generate insights
# if st.session_state.dom_content:
#     st.write("Parsing the profile data...")
#     parsed_result = parse_with_ollama(st.session_state.dom_content)
#     st.session_state.parsed_result = parsed_result

#     st.write("Generating personality insights...")
#     insights = generate_llm_insights(st.session_state.parsed_result)
#     st.session_state.generated_insights = insights
#     st.write("### Personality Insights:")
#     st.write(st.session_state.generated_insights)

# Check for the presence of required keys in the parsed results
if st.session_state.dom_content:
    st.write("Parsing the profile data...")
    parsed_result = parse_with_ollama(st.session_state.dom_content)
    
    # Ensure required keys are present in the parsed result
    required_keys = ['name', 'professional_experiences']
    for key in required_keys:
        if key not in parsed_result:
            parsed_result[key] = "N/A"  # Provide a default value

    st.session_state.parsed_result = parsed_result

    st.write("Generating personality insights...")
    try:
        insights = generate_llm_insights(st.session_state.parsed_result)
        st.session_state.generated_insights = insights
        st.write("### Personality Insights:")
        st.write(st.session_state.generated_insights)
    except Exception as e:
        st.error(f"Error generating insights: {str(e)}")

    # Add thumbs up/down buttons for feedback
    st.write("### Was this insight helpful?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button('👍'):
            st.session_state.user_feedback = 'positive'
            st.success("Thank you for your feedback!")
    with col2:
        if st.button('👎'):
            st.session_state.user_feedback = 'negative'
            st.success("Thank you for your feedback!")

    # Display user feedback if provided
    if st.session_state.user_feedback:
        st.write(f"Your feedback: {st.session_state.user_feedback}")
