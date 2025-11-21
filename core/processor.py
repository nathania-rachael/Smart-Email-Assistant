from database.db import get_connection
from core.prompts import load_prompts
from core.llm_client import call_llm
import json
import re
import time
import sqlite3

def extract_json(text: str):
    if not text:
        return {"category": "Uncategorized", "tasks": []}

    text = re.sub(r"```json|```", "", text).strip()

    try:
        return json.loads(text)
    except:
        return {"category": "Uncategorized", "tasks": []}


def clean_category(label: str):
    if not label:
        return ""
    return label.lower().replace("-", "").replace(" ", "").strip()


def process_all_emails():

    conn = get_connection()
    cursor = conn.cursor()

    prompts = load_prompts()
    cat_prompt = prompts["categorization_prompt"]
    action_prompt = prompts["action_item_prompt"]

    # -----------------------------
    # MERGED PROMPT
    # -----------------------------
    merged_prompt = f"""
You are an intelligent email processing agent.

You must return a JSON response ONLY.

------------------------------------------------------------
TASKS TO DO (COMBINED INTO ONE CALL)
------------------------------------------------------------
1. Use THIS Categorization Prompt:
{cat_prompt}

2. Use THIS Action Item Extraction Prompt:
{action_prompt}

------------------------------------------------------------
OUTPUT FORMAT (VERY IMPORTANT)
------------------------------------------------------------
Return ONLY a JSON object in this exact structure:

{{
  "category": "<email category here>",
  "tasks": [
      {{
         "task": "<task name>",
         "deadline": "<due date>"
      }}
  ]
}}

Rules:
- If no tasks exist, return "tasks": []
- Do NOT include explanations.
- Do NOT add any text outside JSON.
- No markdown, no backticks.
------------------------------------------------------------
"""

    cursor.execute("SELECT * FROM emails")
    emails = cursor.fetchall()

    if not emails:
        conn.close()
        return 0

    processed_count = 0

    for email in emails:
        (
            email_id,
            sender,
            subject,
            timestamp,
            body,
            stored_category,
            stored_actions,
            processed_flag
        ) = email

        email_text = f"Subject: {subject}\nFrom: {sender}\n\n{body}"

        time.sleep(0.2)

        # -------------------------
        # ONE LLM CALL
        # -------------------------
        llm_output = call_llm(
            system_prompt=merged_prompt,
            user_prompt=email_text
        )

        result = extract_json(llm_output)

        category_output = result.get("category", "Uncategorized")
        tasks = result.get("tasks", [])

        action_json_str = json.dumps({"tasks": tasks})

        # -------------------------
        # SAFE DB WRITE (RETRY)
        # -------------------------
        saved = False
        attempts = 0

        while not saved and attempts < 5:
            try:
                cursor.execute(
                    """
                    UPDATE emails
                    SET category = ?, action_items = ?, processed = 1
                    WHERE id = ?
                    """,
                    (category_output, action_json_str, email_id)
                )

                conn.commit()
                saved = True

            except sqlite3.OperationalError:
                attempts += 1
                time.sleep(0.3)

        processed_count += 1
        time.sleep(0.2)

    conn.close()
    return processed_count
