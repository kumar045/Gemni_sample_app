import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

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
                st.code(result, language="html")
            elif input_type == "Image Upload" and uploaded_file and prompt:
                with st.spinner("Generating component..."):
                    image_bytes = uploaded_file.getvalue()
                    image = Image.open(io.BytesIO(image_bytes))
                    result = generate_component(model, prompt, image)
                st.code(result, language="html")
            else:
                st.warning("Please provide all required inputs.")

if __name__ == "__main__":
    main()
