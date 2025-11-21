import json

PROMPTS_FILE = "assets/prompts.json"

def load_prompts():
    with open(PROMPTS_FILE, "r") as f:
        return json.load(f)

def save_prompts(prompts_dict):
    with open(PROMPTS_FILE, "w") as f:
        json.dump(prompts_dict, f, indent=4)
