import streamlit as st
import os
from litellm import completion
import sys
from io import StringIO

class Interpreter:
    def __init__(self):
        self.llm = type('LLM', (), {})()
        self.llm.model = "gemini/gemini-1.5-pro"
        self.llm.temperature = 0
        self.llm.context_window = 16000
        self.llm.max_tokens = 1000
        self.llm.max_output = 1000
        self.llm.api_base = None
        self.llm.api_key = None
        self.llm.api_version = None
        self.llm.supports_functions = True
        self.llm.supports_vision = False
        self.custom_instructions = ""
        self.verbose = False
        self.safe_mode = 'ask'

interpreter = Interpreter()

def setup_environment():
    """Set up the environment with the API key."""
    if interpreter.llm.api_key:
        os.environ['GEMINI_API_KEY'] = interpreter.llm.api_key

def generate_response(prompt, conversation_history):
    """Generate a response using Gemini via LiteLLM."""
    messages = conversation_history + [{"role": "user", "content": prompt}]
    
    response = completion(
        model=interpreter.llm.model,
        messages=messages,
        stream=True,
        temperature=interpreter.llm.temperature,
        max_tokens=interpreter.llm.max_tokens,
        api_base=interpreter.llm.api_base,
        api_key=interpreter.llm.api_key,
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
    st.title("Open Interpreter with Gemini")

    # Sidebar for configuration
    st.sidebar.header("Configuration")
    interpreter.llm.model = st.sidebar.selectbox("Model", ["gemini/gemini-1.5-pro", "gpt-3.5-turbo", "gpt-4"])
    interpreter.llm.temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.0)
    interpreter.llm.max_tokens = st.sidebar.number_input("Max Tokens", 1, 2000, 1000)
    interpreter.llm.api_key = st.sidebar.text_input("API Key", type="password")
    interpreter.llm.api_base = st.sidebar.text_input("API Base URL", "")
    interpreter.llm.supports_functions = st.sidebar.checkbox("Supports Functions", True)
    interpreter.llm.supports_vision = st.sidebar.checkbox("Supports Vision", False)
    interpreter.verbose = st.sidebar.checkbox("Verbose Mode", False)
    interpreter.safe_mode = st.sidebar.selectbox("Safe Mode", ['off', 'ask', 'auto'])

    setup_environment()

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
                if interpreter.safe_mode == 'ask':
                    if st.button("Execute Code"):
                        st.write("Output:")
                        output = execute_code(code)
                        st.text(output)
                elif interpreter.safe_mode == 'auto':
                    st.write("Output:")
                    output = execute_code(code)
                    st.text(output)
                # If safe_mode is 'off', we don't execute the code automatically

        if interpreter.verbose:
            st.write("Debug Information:")
            st.json({
                "Model": interpreter.llm.model,
                "Temperature": interpreter.llm.temperature,
                "Max Tokens": interpreter.llm.max_tokens,
                "Supports Functions": interpreter.llm.supports_functions,
                "Supports Vision": interpreter.llm.supports_vision,
                "Safe Mode": interpreter.safe_mode
            })

if __name__ == "__main__":
    main()
