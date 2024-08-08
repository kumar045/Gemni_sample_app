import streamlit as st
from interpreter import interpreter  # Ensure this module is configured to use Gemini

# Configure Streamlit page
st.set_page_config(
    page_title="Open-Interpreter GPT App",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Title of the app
st.title("💬 Open Interpreter")

# Initialize session state variables if not already present
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Sidebar for API key input
def submit(api_key):
    try:
        # Update interpreter with API key and initialize
        interpreter.llm.api_key = api_key
        interpreter.model = "gemini/gemini-1.5-pro"  # Set the Gemini model
        interpreter.auto_run = True
        
        # Test API key (this is a placeholder; adjust as needed for Gemini)
        response = interpreter.chat("Hello!")
        if not response:
            raise ValueError("Invalid API key or response error.")
    except Exception as e:
        st.error(f"API key test failed: {e}")
        st.info("Please enter a valid Gemini API key to continue.")

# Get API key from sidebar
api_key = st.sidebar.text_input('Gemini API Key', key='widget', type="password")
if api_key:
    submit(api_key)

# Display chat messages
for msg in st.session_state['messages']:
    if msg["role"] == "user":
        st.chat_message(msg["role"]).text(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message(msg["role"]).markdown(msg["content"])

# Handle user input
if prompt := st.chat_input(placeholder="Write here your message", disabled=not api_key):
    st.chat_message("user").text(prompt)
    st.session_state['messages'].append({"role": "user", "content": prompt})

    # Process AI response
    interpreter.model = "gemini/gemini-1.5-pro"
    interpreter.auto_run = True
    full_response = ""
    codeb = True
    outputb = False
    message_placeholder = st.empty()

    try:
        for chunk in interpreter.chat(prompt, display=False, stream=True):
            # Build response
            if "message" in chunk:
                full_response += chunk["message"]
                if chunk['message'] == ":":
                    full_response += "\n"

            if "code" in chunk:
                if full_response.endswith("```"):
                    if chunk['code'].find("\n") != -1 and codeb:
                        partido = full_response[:len(full_response)-3].split("```")[-1]
                        full_response = full_response.replace("```" + partido, "\n```\n" + partido + chunk['code'])
                        codeb = False
                    else:
                        full_response = full_response[:len(full_response)-3] + chunk['code'] + "```"
                else:
                    full_response += f"```{chunk['code']}```"

            if "executing" in chunk:
                if full_response.endswith("```") and full_response[:len(full_response)-3].split("```")[-1].find("\n") != -1:
                    full_response = full_response[:len(full_response)-3] + "\n```"
                full_response += f"\n\n```{chunk['executing']['language']}\n{chunk['executing']['code']}\n```"

            if "output" in chunk:
                if chunk["output"] != "KeyboardInterrupt" and outputb:
                    full_response = full_response[:len(full_response)-4] + chunk['output'] + "\n```\n"
                elif chunk["output"] != "KeyboardInterrupt":
                    full_response += f"\n\n```text\n{chunk['output']}```\n"
                    outputb = True
                codeb = True

            if "end_of_execution" in chunk:
                full_response = full_response.strip()
                full_response += "\n"

            message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        st.session_state['messages'].append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"An error occurred while processing your request: {e}")

# Show message if API key is missing
if not api_key:
    st.info("👋 Hey, we're happy to see you here 🤗")
    st.info("👉 Please enter your Gemini API key to enable code execution.")
    st.error("👉 This project aims to demonstrate a simple implementation of Open Interpreter.")
