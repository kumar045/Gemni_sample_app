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

def extract_and_execute_code(text):
    code_blocks = re.findall(r'```(?:python)?\n(.*?)```', text, re.DOTALL)
    outputs = []
    for code in code_blocks:
        output = io.StringIO()
        sys.stdout = output
        try:
            exec(code)
        except Exception as e:
            print(f"Error: {str(e)}")
        sys.stdout = sys.__stdout__
        outputs.append(output.getvalue())
    return code_blocks, outputs

def main():
    st.title("AI Chat and Code Execution with Open Interpreter")

    # Input for API Key
    api_key = st.text_input("Enter your Google AI Studio API Key:", type="password")
    
    if api_key:
        interpreter.api_key = api_key
        interpreter.model = "gemini-pro"  # Use Gemini Pro model
        
        # Chat interface
        st.subheader("Chat with AI")
        user_input = st.text_area("Enter your message:")
        
        if st.button("Send"):
            if user_input:
                with st.spinner("AI is thinking..."):
                    # Get AI response
                    response = interpreter.chat(user_input)
                    
                    # Display AI response
                    st.write("AI Response:")
                    st.write(response)
                    
                    # Extract, execute, and display code and its output
                    code_blocks, outputs = extract_and_execute_code(response)
                    
                    if code_blocks:
                        for i, (code, output) in enumerate(zip(code_blocks, outputs)):
                            st.subheader(f"Code Block {i+1}:")
                            st.code(code, language="python")
                            st.subheader(f"Output {i+1}:")
                            st.code(output)
            else:
                st.warning("Please enter a message.")
    else:
        st.warning("Please enter your Google AI Studio API Key to start.")

if __name__ == "__main__":
    main()
