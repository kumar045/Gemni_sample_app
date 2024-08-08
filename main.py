import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import re
import json

def initialize_gemini_client(api_key):
    """Initialize the Google Gemini client with the provided API key."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name="gemini-1.5-pro-exp-0801")

def generate_component(model, prompt, image=None):
    """Generate a React component based on the prompt and/or image."""
    chat_session = model.start_chat(history=[])
    
    full_prompt = f"""
    Create a React functional component based on the following description:
    {prompt}
    
    Please provide the component as a complete React functional component using hooks if necessary.
    Use inline styles or a separate styles object for CSS.
    Ensure the component is self-contained and can be rendered directly.
    Include comments to explain the component structure and any complex logic.
    
    Format the response as a JSON object with two keys:
    1. "component": The full React component code as a string.
    2. "explanation": A brief explanation of the component's functionality and any notes on usage.
    """
    
    if image:
        response = chat_session.send_message([full_prompt, image])
    else:
        response = chat_session.send_message(full_prompt)
    
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"component": response.text, "explanation": "Unable to parse explanation."}

def main():
    st.title("React Component Generator")

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
            st.subheader("Generated React Component:")
            st.code(result["component"], language="jsx")

            # Display the explanation
            st.subheader("Component Explanation:")
            st.write(result["explanation"])

            # Render the React component
            st.subheader("Generated UI:")
            st.components.v1.html(f"""
                <div id="react-root"></div>
                <script src="https://unpkg.com/react@17/umd/react.development.js"></script>
                <script src="https://unpkg.com/react-dom@17/umd/react-dom.development.js"></script>
                <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
                <script type="text/babel">
                    {result["component"]}
                    ReactDOM.render(<Component />, document.getElementById('react-root'));
                </script>
            """, height=400, scrolling=True)

if __name__ == "__main__":
    main()
