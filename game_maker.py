import openai
import subprocess
import re
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_python_code(text):
    pattern = r"```python\s*(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    
    if matches:
        code = "\n\n".join(match.strip() for match in matches)
    else:
        code = text.strip()
    
    return code

def ask_chatgpt_for_code(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    raw_text = response.choices[0].message.content
    return extract_python_code(raw_text)

def save_code_to_file(code, filename="game.py"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)

def run_code_and_capture_errors(filename="game.py"):
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

