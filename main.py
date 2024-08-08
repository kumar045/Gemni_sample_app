import streamlit as st
from interpreter import interpreter
import google.generativeai as genai
from PIL import Image
import io

def setup_gemini(api_key):
    """Configure Gemini settings."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    return model

def generate_react_component(model, prompt, image=None):
    """Generate a React component using Gemini."""
    full_prompt = f"""
    Create a React functional component based on the following description:
    {prompt}
    
    Use inline styles for CSS to ensure the component is fully self-contained.
    Name the component 'GeneratedComponent'.
    Include comments to explain the component structure and any complex logic.
    After defining the component, provide code to render it to a div with id 'react-root'.
    
    Return the full code including the component definition and the rendering code.
    """
    
    if image:
        response = model.generate_content([full_prompt, image])
    else:
        response = model.generate_content(full_prompt)
    
    return response.text

def main():
    st.title("React Component Generator with Gemini")

    # Input for API key
    api_key = st.sidebar.text_input("Enter your Google AI API Key:", type="password")
    
    if not api_key:
        st.warning("Please enter your Google AI API Key in the sidebar to proceed.")
        return

    model = setup_gemini(api_key)

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
        if (input_type == "Text Prompt" and prompt) or (input_type == "Image Upload" and uploaded_file and prompt):
            with st.spinner("Generating component..."):
                if input_type == "Image Upload":
                    image_bytes = uploaded_file.getvalue()
                    image = Image.open(io.BytesIO(image_bytes))
                    result = generate_react_component(model, prompt, image)
                else:
                    result = generate_react_component(model, prompt)

            # Display the generated code
            st.subheader("Generated React Component:")
            st.code(result, language="jsx")

            # Render the React component
            st.subheader("Live Preview:")
            st.components.v1.html(f"""
                <div id="react-root"></div>
                <script src="https://unpkg.com/react@17/umd/react.development.js"></script>
                <script src="https://unpkg.com/react-dom@17/umd/react-dom.development.js"></script>
                <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
                <script type="text/babel">
                    {result}
                </script>
            """, height=600, scrolling=True)
        else:
            st.warning("Please provide all required inputs.")

if __name__ == "__main__":
    main()
