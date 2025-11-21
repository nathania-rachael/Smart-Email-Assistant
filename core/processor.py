from database.db import get_connection
from core.prompts import load_prompts
from core.llm_client import call_llm
import json
import re
import time

def extract_json(text: str):
    """Extract clean JSON from Gemini output."""
    if not text:
        return {"tasks": []}

    # Remove code block formatting if present
    text = re.sub(r"```json|```", "", text).strip()

    # Attempt JSON parsing
    try:
        return json.loads(text)
    except:
        return {"tasks": []}


def clean_category(label: str):
    """
    Standardize category text for comparison:
    'To-Do', 'todo', 'TO DO', etc. → 'todo'
    """
    if not label:
        return ""
    return label.lower().replace("-", "").replace(" ", "").strip()


def process_all_emails():

    conn = get_connection()
    cursor = conn.cursor()

    prompts = load_prompts()
    cat_prompt = prompts["categorization_prompt"]
    action_prompt = prompts["action_item_prompt"]

    cursor.execute("SELECT * FROM emails")
    emails = cursor.fetchall()

    if not emails:
        conn.close()
        return 0

    processed_count = 0

    # Allowed categories for action-item extraction
    ACTIONABLE = {"todo", "projectupdate", "reminder"}

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

        # ---------- 1. CATEGORIZE EMAIL ----------
        category_output = call_llm(
            system_prompt=cat_prompt,
            user_prompt=email_text
        ).strip()

        time.sleep(0.5)

        cat_key = clean_category(category_output)

        # ---------- 2. ACTION ITEMS (only for actionable categories) ----------
        if cat_key in ACTIONABLE:
            ai_output = call_llm(
                system_prompt=action_prompt,
                user_prompt=email_text
            )

            time.sleep(0.5)

            action_json = extract_json(ai_output)
        else:
            action_json = {"tasks": []}

        # Convert action JSON to string for saving
        action_json_str = json.dumps(action_json)

        # ---------- 3. SAVE BACK INTO DATABASE ----------
        cursor.execute(
            """
            UPDATE emails
            SET category = ?, action_items = ?, processed = 1
            WHERE id = ?
            """,
            (category_output, action_json_str, email_id)
        )

        processed_count += 1

    conn.commit()
    conn.close()
    return processed_count
