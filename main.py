import streamlit as st
from interpreter import interpreter
from litellm import completion
import os

def check_api_key(api_key):
    """Check if the API key is available."""
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
        st.stop()
    os.environ['GEMINI_API_KEY'] = api_key

def chat_with_gemini(prompt):
    """Generate a response from the Gemini model based on a given prompt."""
    response = completion(
        model="gemini/gemini-pro",
        messages=[{"role": "user", "content": prompt}],
    )
    if response and response.choices:
        return response.choices[0].message.content
    else:
        return "No response from the model"

def custom_gemini_model(messages):
    """
    Custom language model function using Gemini Pro via LiteLLM.
    This function is compatible with Open Interpreter's expected format.
    """
    # Combine all messages into a single prompt
    full_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
    
    response = chat_with_gemini(full_prompt)
    
    yield {"delta": {"role": "assistant"}}
    for chunk in response:
        yield {"delta": {"content": chunk}}

def initialize_interpreter():
    """Initialize Open Interpreter with custom Gemini model."""
    interpreter.llm.model = "custom"
    interpreter.llm.custom_llm_provider = custom_gemini_model
    interpreter.auto_run = False  # For safety, require user confirmation
    interpreter.conversation_history = True
    interpreter.chat_history = []

def chat_with_interpreter(user_input):
    """Send user input to Open Interpreter and return the response."""
    return interpreter.chat(user_input, stream=True, display=False)

def main():
    st.title("Open Interpreter with Gemini Pro (via LiteLLM)")

    # Sidebar for API key input
    api_key = st.sidebar.text_input("Enter your Gemini API Key:", type="password")
    check_api_key(api_key)

    # Initialize Open Interpreter
    initialize_interpreter()

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
