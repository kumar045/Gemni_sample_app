import streamlit as st
from interpreter import interpreter
import io
import sys
import re

def capture_output(func):
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    result = func()
    output = new_stdout.getvalue()
    sys.stdout = old_stdout
    return result, output

def extract_code_and_output(text):
    # Extract code blocks
    code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', text, re.DOTALL)
    
    # Remove code blocks from the text to get the rest as output
    output = re.sub(r'```(?:\w+)?\n.*?```', '', text, flags=re.DOTALL).strip()
    
    return code_blocks, output

def main():
    st.title("AI Chat and Code Execution with Open Interpreter")

    # Input for API Key
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    
    if api_key:
        interpreter.llm.api_key = api_key
        interpreter.llm.model = "gemini/gemini-1.5-pro"
        
        # Chat interface
        st.subheader("Chat with AI")
        user_input = st.text_area("Enter your message:")
        
        if st.button("Send"):
            if user_input:
                with st.spinner("AI is thinking..."):
                    # Capture the output of the interpreter
                    response, captured_output = capture_output(lambda: interpreter.chat(user_input))
                    
                    # Display AI response
                    st.write("AI Response:")
                    st.write(response)
                    
                    # Extract and display executed code and its output
                    code_blocks, output = extract_code_and_output(captured_output)
                    
                    if code_blocks:
                        st.subheader("Executed Code:")
                        for code in code_blocks:
                            st.code(code)
                    
                    if output:
                        st.subheader("Code Output:")
                        st.code(output)
            else:
                st.warning("Please enter a message.")
    else:
        st.warning("Please enter your OpenAI API Key to start.")

if __name__ == "__main__":
    main()
