import streamlit as st
import io
import sys
import re
from streamlit.components.v1 import html
from streamlit_extras.add_vertical_space import add_vertical_space
import interpreter  # Ensure this module is configured to use Gemini

# Initialize session state variables if not already present
if 'Gemini_api_key' not in st.session_state:
    st.session_state.Gemini_api_key = ''
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Configure Streamlit page
st.set_page_config(
    page_title="Open-Interpreter GPT App",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Title of the app
st.title("💬 Open Interpreter")

# Sidebar with API key input
with st.sidebar:
    def submit():
        try:
            st.session_state.Gemini_api_key = st.session_state.widget
            interpreter.api_key = st.session_state.Gemini_api_key
            interpreter.model = "gemini/gemini-1.5-pro"  # Set the Gemini model
            # Test API key (this is a placeholder; adjust as needed for Gemini)
            response = interpreter.chat("Hello!")
            if not response:
                raise ValueError("Invalid API key or response error.")
        except Exception as e:
            st.write(e)
            st.session_state.widget = ''
            st.session_state.Gemini_api_key = ''
            st.info("Please enter a valid Gemini API key to continue.")

    st.text_input('Gemini API Key', key='widget', on_change=submit, type="password")

    # Additional sidebar content
    add_vertical_space(29)
    st.markdown(
        '<center><h5>🤗 Support the project with a donation for new features 🤗</h5>', 
        unsafe_allow_html=True
    )
    button = (
        '<script type="text/javascript" '
        'src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" '
        'data-name="bmc-button" '
        'data-slug="blazzmocompany" '
        'data-color="#FFDD00" '
        'data-emoji="" '
        'data-font="Cookie" '
        'data-text="Buy me a coffee" '
        'data-outline-color="#000000" '
        'data-font-color="#000000" '
        'data-coffee-color="#ffffff"></script>'
    )
    html(button, height=70, width=220)
    iframe = (
        '<style>iframe[width="220"]{position: absolute; top: 50%; left: 50%; '
        'transform: translate(-50%, -50%); margin:26px 0}</style>'
    )
    st.markdown(iframe, unsafe_allow_html=True)
    add_vertical_space(2)
    st.write(
        '<center><h6>Made with ❤️ by <a href="mailto:blazzmo.company@gmail.com">AI-Programming</a></h6>', 
        unsafe_allow_html=True
    )

# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message(msg["role"]).text(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message(msg["role"]).markdown(msg["content"])

# Handle user input
if prompt := st.chat_input(placeholder="Write here your message", disabled=not st.session_state.Gemini_api_key):
    st.chat_message("user").text(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Process AI response
    interpreter.model = "gemini-pro"
    full_response = ""
    codeb = True
    outputb = False
    message_placeholder = st.empty()

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

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Show message if API key is missing
elif not st.session_state.Gemini_api_key:
    st.info("👋 Hey, we're happy to see you here 🤗")
    st.info("👉 Please enter your Gemini API key to enable code execution.")
    st.error("👉 This project aims to demonstrate a simple implementation of Open Interpreter.")
