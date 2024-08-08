import streamlit as st
from interpreter import interpreter
import io
import sys

def capture_output(func):
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    result = func()
    output = new_stdout.getvalue()
    sys.stdout = old_stdout
    return result, output

def main():
    st.title("AI Chat and Code Execution with Open Interpreter")

    # Input for API Key
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    
    if api_key:
        interpreter.llm.api_key = api_key
        interpreter.llm.model = "gemini/gemini-1.5-pro"
        interpreter.auto_run =  True
        
        # Chat interface
        st.subheader("Chat with AI")
        user_input = st.text_area("Enter your message:")
        
        if st.button("Send"):
            if user_input:
                with st.spinner("AI is thinking..."):
                    # Capture the output of the interpreter
                    response, output = capture_output(lambda: interpreter.chat(user_input))
                    
                    # Display AI response
                    st.write("AI Response:")
                    st.write(response)
                    
                    # Display any output (including executed code and its result)
                    if output.strip():
                        st.subheader("Code Execution Output:")
                        st.code(output)
            else:
                st.warning("Please enter a message.")
    else:
        st.warning("Please enter your Gemini Key to start.")

if __name__ == "__main__":
    main()
