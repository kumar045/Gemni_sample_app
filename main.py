import streamlit as st
from interpreter import interpreter
import google.generativeai as genai
from PIL import Image
import io

def setup_gemini(api_key):
    """Configure Gemini settings."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')

def custom_gemini_model(messages):
    """
    Custom language model function using Gemini.
    This function is compatible with Open Interpreter's expected format.
    """
    # Convert Open Interpreter message format to Gemini format
    gemini_messages = [
        {"role": msg["role"], "parts": [msg["content"]]}
        for msg in messages
    ]
    
    # Get the last user message
    last_user_message = gemini_messages[-1]["parts"][0]

    # Generate content using Gemini
    response = model.generate_content(last_user_message)

    # Yield the assistant role first
    yield {"delta": {"role": "assistant"}}

    # Then yield the content
    for chunk in response.text:
        yield {"delta": {"content": chunk}}

def initialize_interpreter(model):
    """Initialize Open Interpreter with custom Gemini model."""
    interpreter.model = "custom"  # Use custom model
    interpreter.custom_llm = custom_gemini_model  # Set the custom model function
    interpreter.auto_run = False  # For safety, require user confirmation
    interpreter.conversation_history = True
    interpreter.chat_history = []  # Initialize chat history

def chat_with_interpreter(user_input):
    """Send user input to Open Interpreter and return the response."""
    response = interpreter.chat(user_input, stream=True)
    return response

def main():
    st.title("Open Interpreter with Gemini")

    # Initialize session state for chat history if it doesn't exist
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Sidebar for configuration
    st.sidebar.header("Configuration")
    api_key = st.sidebar.text_input("Enter your Google AI API Key:", type="password")
    
    if api_key:
        global model
        model = setup_gemini(api_key)
        initialize_interpreter(model)

        # Chat interface
        st.write("Chat with Open Interpreter powered by Gemini. Type 'exit' to end the conversation.")

        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # User input
        user_input = st.chat_input("Your message:")

        if user_input:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # Display user message
            with st.chat_message("user"):
                st.write(user_input)

            # Get and display Open Interpreter response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for chunk in chat_with_interpreter(user_input):
                    if chunk.get("content"):
                        full_response += chunk["content"]
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)

            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})
    else:
        st.warning("Please enter your Google AI API Key in the sidebar to start chatting.")

if __name__ == "__main__":
    main()
