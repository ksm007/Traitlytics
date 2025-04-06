import streamlit as st
import streamlit.components.v1 as components
import re
from scrape import scrape_website
from llm_insights import generate_llm_insights, parse_llm_response

def clean_markdown(text):
    """
    Remove Markdown-style bold formatting and clean extra whitespace.
    """
    cleaned_text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # Remove bold formatting
    cleaned_text = re.sub(r"\n{2,}", "\n", cleaned_text).strip()  # Remove extra newlines
    cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text)  # Remove extra spaces
    return cleaned_text

def display_insights(insights):
    """
    Display the insights in a user-friendly format.
    """
    if "DISC_Personality_Type" in insights:
        st.subheader("DISC Personality Type")
        st.markdown(insights["DISC_Personality_Type"])
    
    if "Profile_Summary" in insights:
        st.subheader("Profile Summary")
        st.markdown(insights["Profile_Summary"])
    
    if "Personality_Diagram" in insights:
        st.subheader("Personality Diagram")
        st.markdown(insights["Personality_Diagram"])
    
    if "Key_Traits" in insights:
        st.subheader("Key Traits")
        for trait in insights["Key_Traits"]:
            st.write(trait)
    
    if "Dos" in insights:
        st.subheader("Dos")
        for suggestion in insights["Dos"]:
            st.write(suggestion)
    
    if "Donts" in insights:
        st.subheader("Don'ts")
        for suggestion in insights["Donts"]:
            st.write(suggestion)

def redirect_button(url: str, text: str = None, color: str = "#FD504D"):
    """
    Render a styled redirect button that navigates the user to the provided URL.
    """
    st.markdown(
        f"""
        <a href="{url}" target="_blank">
            <div style="
                display: inline-block;
                padding: 0.5em 1em;
                color: #FFFFFF;
                background-color: {color};
                border-radius: 3px;
                text-decoration: none;">
                {text}
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )

def main():
    st.title("Web Scraping and LLM Insights")
    website_url = st.text_input("Enter website URL to scrape:")

    if st.button("Scrape"):
        if not website_url:
            st.error("URL is required!")
        else:
            try:
                st.info("Scraping website...")
                # Step 1: Scrape profile data (used internally; not displayed)
                profile_data = scrape_website(website_url)
                
                if not profile_data or not any(profile_data.values()):
                    st.error("Failed to scrape content or insufficient data from the provided URL.")
                    return

                st.info("Generating insights...")
                # Step 2: Generate LLM insights
                insights = generate_llm_insights(profile_data)
                
                # Step 3: Clean and parse insights
                cleaned_insights = clean_markdown(insights)
                structured_response = parse_llm_response(cleaned_insights)
                st.success("Insights generated successfully!")
                
                # Step 4: Display the structured insights in a friendly format
                display_insights(structured_response)
                
                # Step 5: Show a redirect button to take the user to another page
                redirect_url = "https://docs.google.com/forms/d/e/1FAIpQLScC5gweNmfbj1M9fpKOXYgWddYkR9h37kGqIybmkukK7JEdtw/viewform?usp=dialog"
                redirect_button(redirect_url, text="Go to Form", color="#FD504D")
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
