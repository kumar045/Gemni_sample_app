import streamlit as st
import os
from litellm import completion
import sys
from io import StringIO

def setup_environment(api_key):
    """Set up the environment with the API key."""
    os.environ['GEMINI_API_KEY'] = api_key

def generate_response(prompt, conversation_history):
    """Generate a response using Gemini via LiteLLM."""
    messages = conversation_history + [{"role": "user", "content": prompt}]
    
    response = completion(
        model="gemini/gemini-1.5-pro",
        messages=messages,
        stream=True
    )
    
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
            yield chunk.choices[0].delta.content
    
    return full_response

def execute_code(code):
    """Execute the generated Python code and capture the output."""
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    try:
        exec(code, globals())
        sys.stdout = old_stdout
        return redirected_output.getvalue()
    except Exception as e:
        sys.stdout = old_stdout
        return f"Error executing code: {str(e)}"

def main():
    st.title("Gemini Code Interpreter with LiteLLM")

    # Sidebar for API key input
    api_key = st.sidebar.text_input("Enter your Gemini API Key:", type="password")
    if api_key:
        setup_environment(api_key)
    else:
        st.warning("Please enter your Gemini API Key in the sidebar to start.")
        return

    # Initialize session state
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    # Display conversation history
    for message in st.session_state.conversation_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    user_input = st.chat_input("You:")

    if user_input:
        # Add user message to chat history
        st.session_state.conversation_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for chunk in generate_response(user_input, st.session_state.conversation_history):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.conversation_history.append({"role": "assistant", "content": full_response})

        # Check if the response contains Python code
        if "```python" in full_response:
            code_blocks = full_response.split("```python")
            for block in code_blocks[1:]:
                code = block.split("```")[0].strip()
                st.code(code, language="python")
                st.write("Output:")
                output = execute_code(code)
                st.text(output)

if __name__ == "__main__":
    main()
