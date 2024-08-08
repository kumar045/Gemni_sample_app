import streamlit as st
import google.generativeai as genai
import os

def setup_gemini(api_key):
    """Configure Gemini settings."""
    os.environ['GOOGLE_API_KEY'] = api_key
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-pro')

def chat_with_gemini(model, message, chat_history):
    """Generate a response from Gemini based on the chat history and new message."""
    messages = [
        {'role': 'user' if msg['role'] == 'user' else 'model', 'parts': [msg['content']]}
        for msg in chat_history
    ]
    messages.append({'role': 'user', 'parts': [message]})
    
    response = model.generate_content(messages, stream=True)
    return response

def main():
    st.title("Gemini Chat Application")

    # Sidebar for API key input
    api_key = st.sidebar.text_input("Enter your Google AI API Key:", type="password")
    
    if not api_key:
        st.warning("Please enter your Google AI API Key in the sidebar to start chatting.")
        return

    # Initialize Gemini model
    model = setup_gemini(api_key)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("What would you like to know?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Gemini response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for chunk in chat_with_gemini(model, prompt, st.session_state.messages):
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
