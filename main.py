import streamlit as st
from interpreter import interpreter

def main():
    st.title("AI Chat and Code Execution with Open Interpreter")

    # Input for API Key
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    
    if api_key:
        interpreter.llm.api_key = api_key
        interpreter.llm.model = "gemini/gemini-1.5-pro"
        interpreter.auto_run = True
        
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
            else:
                st.warning("Please enter a message.")
    else:
        st.warning("Please enter your OpenAI API Key to start.")

if __name__ == "__main__":
    main()
