import streamlit as st
from interpreter import interpreter
import google.generativeai as genai

def setup_gemini(api_key):
    """Configure Gemini 1.5 Pro settings with code execution."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name='gemini-1.5-pro', tools='code_execution')

def custom_gemini_model(messages):
    """
    Custom language model function using Gemini 1.5 Pro with code execution.
    This function is compatible with Open Interpreter's expected format.
    """
    # Convert messages to Gemini format
    gemini_messages = []
    for msg in messages:
        if msg['role'] == 'system':
            gemini_messages.append({"role": "user", "parts": [msg['content']]})
        else:
            gemini_messages.append({"role": msg['role'], "parts": [msg['content']]})
    
    response = model.generate_content(gemini_messages, stream=True)

    yield {"delta": {"role": "assistant"}}
    for chunk in response:
        if chunk.text:
            yield {"delta": {"content": chunk.text}}
        if chunk.candidates:
            for candidate in chunk.candidates:
                if candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.function_call:
                            yield {"delta": {"content": f"\nFunction Call: {part.function_call.name}\n"}}
                            yield {"delta": {"content": f"Arguments: {part.function_call.args}\n"}}
                        elif part.text:
                            yield {"delta": {"content": part.text}}

def initialize_interpreter(model):
    """Initialize Open Interpreter with custom Gemini 1.5 Pro model."""
    interpreter.llm.model = "custom"
    interpreter.llm.custom_llm_provider = custom_gemini_model
    interpreter.auto_run = True  # Enable auto-run for code execution
    interpreter.conversation_history = True
    interpreter.chat_history = []

def chat_with_interpreter(user_input):
    """Send user input to Open Interpreter and return the response."""
    return interpreter.chat(user_input, stream=True, display=False)

def main():
    st.title("Open Interpreter with Gemini 1.5 Pro")

    # Sidebar for API key input
    api_key = st.sidebar.text_input("Enter your Google AI API Key:", type="password")
    
    if not api_key:
        st.warning("Please enter your Google AI API Key in the sidebar to start chatting.")
        return

    # Initialize Gemini and Open Interpreter
    global model
    model = setup_gemini(api_key)
    initialize_interpreter(model)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("What would you like to do?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Open Interpreter response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for chunk in chat_with_interpreter(prompt):
                if chunk["type"] == "message":
                    full_response += chunk["content"]
                    message_placeholder.markdown(full_response + "▌")
                elif chunk["type"] == "code":
                    full_response += f"\n```python\n{chunk['content']}\n```\n"
                    message_placeholder.markdown(full_response + "▌")
                elif chunk["type"] == "output":
                    full_response += f"\nOutput: {chunk['content']}\n"
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
