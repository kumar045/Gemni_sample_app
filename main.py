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
    print("AI Chat and Code Execution with Open Interpreter")
    
    # Input for API Key
    api_key = input("Enter your Google AI Studio API Key: ")
    
    if api_key:
        interpreter.llm.api_key = api_key
        interpreter.auto_run = True
        interpreter.llm.model = "gemini/gemini-1.5-flash"  # Use Gemini Pro model
        
        while True:
            # Chat interface
            print("\nChat with AI")
            user_input = input("Enter your message (or 'quit' to exit): ")
            
            if user_input.lower() == 'quit':
                break
            
            if user_input:
                print("AI is thinking...")
                # Get AI response
                response = interpreter.chat(user_input)
                
                # Display AI response
                print("AI Response:")
                print(response)
                
                # Extract, execute, and display code and its output
                code_blocks, outputs = extract_and_execute_code(response)
                
                if code_blocks:
                    for i, (code, output) in enumerate(zip(code_blocks, outputs)):
                        print(f"\nCode Block {i+1}:")
                        print(code)
                        print(f"\nOutput {i+1}:")
                        print(output)
            else:
                print("Please enter a message.")
    else:
        print("Please enter your Google AI Studio API Key to start.")

if __name__ == "__main__":
    main()
