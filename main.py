import os
from litellm import completion
import json

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
            print(chunk.choices[0].delta.content, end='', flush=True)
    print()  # New line after full response
    
    return full_response

def execute_code(code):
    """Execute the generated Python code."""
    try:
        exec(code, globals())
    except Exception as e:
        print(f"Error executing code: {str(e)}")

def interpreter_loop():
    """Main interpreter loop."""
    conversation_history = []
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        
        response = generate_response(user_input, conversation_history)
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": response})
        
        # Check if the response contains Python code
        if "```python" in response:
            code_blocks = response.split("```python")
            for block in code_blocks[1:]:
                code = block.split("```")[0].strip()
                print("\nExecuting code:")
                print(code)
                print("\nOutput:")
                execute_code(code)

if __name__ == "__main__":
    api_key = input("Enter your Gemini API Key: ")
    setup_environment(api_key)
    print("Gemini Code Interpreter initialized. Type 'exit' or 'quit' to end the session.")
    interpreter_loop()
