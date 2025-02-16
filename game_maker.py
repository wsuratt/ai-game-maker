import openai
import subprocess
import re

# Set your API key (consider storing this securely, e.g., via an environment variable)
openai.api_key = "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"

def extract_python_code(text):
    """
    Extracts only Python code from text containing markdown code blocks.
    This function will only match code blocks that start with ```python.
    If no such block exists, it returns the full text stripped.
    """
    # This pattern matches code blocks that start with ```python and end with ```
    pattern = r"```python\s*(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    
    if matches:
        # Join all found Python code blocks together after stripping any extra whitespace
        code = "\n\n".join(match.strip() for match in matches)
    else:
        # If no python code block is found, assume the entire text is code
        code = text.strip()
    
    return code

def ask_chatgpt_for_code(prompt):
    """Ask ChatGPT for code based on a prompt, then extract only the Python code."""
    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # or use gpt-3.5-turbo if preferred
        messages=[{"role": "user", "content": prompt}],
        temperature=0  # Low temperature for predictable code output
    )
    # Get the raw text from the API response.
    raw_text = response.choices[0].message.content
    # Extract pure Python code from the raw text.
    return extract_python_code(raw_text)

def save_code_to_file(code, filename="game.py"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)

def run_code_and_capture_errors(filename="game.py"):
    """Runs the code in a subprocess and returns (success, stdout, stderr)."""
    try:
        result = subprocess.run(
            ["python", filename],
            capture_output=True,
            text=True
        )
        success = (result.returncode == 0)
        return success, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

if __name__ == "__main__":
    # 1) Ask the model for a simple Pygame Snake game
    prompt_for_game = (
        "Write a simple Pygame 'Snake' game in Python. "
        "Include collision detection, scoring, and a game-over screen."
    )
    
    code = ask_chatgpt_for_code(prompt_for_game)
    save_code_to_file(code, "game.py")
    
    # 2) Test the code
    success, stdout, stderr = run_code_and_capture_errors("game.py")
    attempt = 1
    
    # We'll iterate a few times if it fails
    while not success and attempt < 5:
        print(f"Attempt #{attempt} failed with errors:\n{stderr}")
        
        # 3) Ask ChatGPT to fix the error based on the captured error message
        fix_prompt = (
            f"I tried to run your Pygame code and got this error:\n{stderr}\n"
            "Please fix the code."
        )
        new_code = ask_chatgpt_for_code(fix_prompt)
        save_code_to_file(new_code, "game.py")

        # Re-run the code
        success, stdout, stderr = run_code_and_capture_errors("game.py")
        attempt += 1
    
    if success:
        print("Game runs successfully! Check out game.py.")
    else:
        print("Could not fix the code automatically after multiple attempts.")
        print("Final error:\n", stderr)

