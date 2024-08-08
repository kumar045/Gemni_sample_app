import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import re

def initialize_gemini_client(api_key):
    """Initialize the Google Gemini client with the provided API key."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name="gemini-1.5-pro-exp-0801")

def generate_component(model, prompt, image=None):
    """Generate a Tailwind CSS component based on the prompt and/or image."""
    chat_session = model.start_chat(history=[])
    
    if image:
        response = chat_session.send_message([prompt, image])
    else:
        response = chat_session.send_message(prompt)
    
    return response.text

def extract_html_and_css(generated_code):
    """Extract HTML and CSS from the generated code."""
    html_pattern = r'<div.*?>([\s\S]*?)<\/div>'
    css_pattern = r'<style>([\s\S]*?)<\/style>'

    html_match = re.search(html_pattern, generated_code, re.DOTALL)
    css_match = re.search(css_pattern, generated_code, re.DOTALL)

    html = html_match.group(0) if html_match else ""
    css = css_match.group(1) if css_match else ""

    return html, css

def main():
    st.title("Tailwind CSS Component Generator")

    # Input for API key
    api_key = st.text_input("Enter your Google Gemini API Key:", type="password")

    if api_key:
        model = initialize_gemini_client(api_key)

        # User input options
        input_type = st.radio("Choose input type:", ["Text Prompt", "Image Upload"])

        if input_type == "Text Prompt":
            prompt = st.text_area("Enter your component description:")
        else:
            uploaded_file = st.file_uploader("Upload an image:", type=["png", "jpg", "jpeg"])
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                prompt = st.text_area("Enter additional details or requirements:")

        if st.button("Generate Component"):
            if input_type == "Text Prompt" and prompt:
                with st.spinner("Generating component..."):
                    result = generate_component(model, prompt)
            elif input_type == "Image Upload" and uploaded_file and prompt:
                with st.spinner("Generating component..."):
                    image_bytes = uploaded_file.getvalue()
                    image = Image.open(io.BytesIO(image_bytes))
                    result = generate_component(model, prompt, image)
            else:
                st.warning("Please provide all required inputs.")
                return

            # Display the generated code
            st.subheader("Generated Code:")
            st.code(result, language="html")

            # Extract and display the component
            html, css = extract_html_and_css(result)
            if html and css:
                st.subheader("Generated Component:")
                st.markdown(f"""
                    <style>
                    {css}
                    </style>
                    {html}
                """, unsafe_allow_html=True)
            else:
                st.warning("Couldn't extract valid HTML and CSS from the generated code.")

if __name__ == "__main__":
    main()
