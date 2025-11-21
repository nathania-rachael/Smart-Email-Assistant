import streamlit as st
from database.db import fetch_all_emails
from core.prompts import load_prompts, save_prompts
from core.processor import process_all_emails
import ast

# ------------------------------------------------------------
# Streamlit Page Config
# ------------------------------------------------------------
st.set_page_config(page_title="OceanAI Email Assistant", layout="wide")
st.markdown("## OceanAI Email Assistant")

# ------------------------------------------------------------
# Initialize Session State
# ------------------------------------------------------------
if "raw_inbox" not in st.session_state:
    st.session_state["raw_inbox"] = None

if "processed_inbox" not in st.session_state:
    st.session_state["processed_inbox"] = None

# For chat histories
if "email_chat_history" not in st.session_state:
    st.session_state["email_chat_history"] = []

if "inbox_chat_history" not in st.session_state:
    st.session_state["inbox_chat_history"] = []

# For reply drafts
if "draft_replies" not in st.session_state:
    st.session_state["draft_replies"] = {}  

# ------------------------------------------------------------
# Sidebar Menu
# ------------------------------------------------------------
page = st.sidebar.radio("Menu", ["Home", "View & Process Mails", "Prompt Editor", "Email Agent"])

# ------------------------------------------------------------
# Sidebar Reply Drafts Section
# ------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### Draft Replies")

if st.session_state["draft_replies"]:
    for email_id, draft in st.session_state["draft_replies"].items():
        with st.sidebar.expander(f"Draft for Email #{email_id}"):
            st.write(draft)
else:
    st.sidebar.write("No drafts available.")

# ============================================================
# HOME / LANDING PAGE
# ============================================================
if page == "Home":
    st.markdown("## Email Productivity Agent")

    st.write(
        """
        Welcome to your Email Productivity Assistant.

        This tool helps you manage your inbox more efficiently by using AI to:
        - Organize and categorize incoming emails  
        - Identify important tasks and deadlines  
        - Provide quick summaries or clarifications  
        - Assist you in drafting replies  
        - Answer queries about a specific email or your entire inbox  
        """
    )

    st.info("Use the sidebar to navigate.")


# ============================================================
# VIEW & PROCESS EMAIL PAGE
# ============================================================
elif page == "View & Process Mails":
    st.markdown("### Mail Inbox")

    col1, col2 = st.columns(2)

    # ---------- LOAD RAW INBOX ----------
    with col1:
        if st.button("Load Inbox"):
            emails_df = fetch_all_emails()

            st.session_state["raw_inbox"] = emails_df[
                ["id", "sender", "subject", "timestamp", "body"]
            ]
            st.session_state["processed_inbox"] = None

            st.success("Loaded raw inbox.")

    # ---------- PROCESS INBOX WITH AI ----------
    with col2:
        if st.button("Process Inbox with AI"):
            with st.spinner("Processing emails using Gemini..."):
                count = process_all_emails()

                processed_df = fetch_all_emails()
                st.session_state["processed_inbox"] = processed_df
                st.session_state["raw_inbox"] = None

            st.success(f"Processed {count} emails successfully!")

    # ---------- DISPLAY EMAILS ----------
    st.subheader("Inbox")

    # ==========================
    #    PROCESSED INBOX VIEW
    # ==========================
    if st.session_state["processed_inbox"] is not None:
        df = st.session_state["processed_inbox"]

        st.markdown("### Processed Emails")

        for _, row in df.iterrows():
            st.markdown("---")

            st.markdown(
                f"""
                **Subject:** {row['subject']}  
                **From:** {row['sender']}  
                **Time:** {row['timestamp']}  
                **Category:** `{row['category']}`  
                """
            )

            with st.expander("View Email Body"):
                st.write(row["body"])

            # --- ACTION ITEMS (only show if tasks exist)
            try:
                data = ast.literal_eval(row["action_items"])
                tasks = data.get("tasks", [])
            except:
                tasks = []

            if tasks:
                with st.expander("Action Items"):
                    for t in tasks:
                        st.markdown(
                            f"- **{t.get('task','')}** (Deadline: {t.get('deadline','')})"
                        )

            # --------- GENERATE REPLY BUTTON ---------
            if st.button(f"Generate Reply for Email #{row['id']}", key=f"reply_processed_{row['id']}"):

                email_text = (
                    f"Subject: {row['subject']}\n"
                    f"From: {row['sender']}\n\n"
                    f"{row['body']}"
                )

                prompts = load_prompts()
                reply_prompt = prompts["auto_reply_prompt"]

                from core.llm_client import call_llm
                reply = call_llm(system_prompt=reply_prompt, user_prompt=email_text)

                st.session_state["draft_replies"][row["id"]] = reply
                st.success("Draft reply saved! Check the sidebar under Draft Replies.")
                st.rerun()

        st.markdown("---")

    # ==========================
    #         RAW VIEW
    # ==========================
    elif st.session_state["raw_inbox"] is not None:
        df = st.session_state["raw_inbox"]

        for _, row in df.iterrows():
            st.markdown("---")

            st.markdown(
                f"""
                **Subject:** {row['subject']}  
                **From:** {row['sender']}  
                **Time:** {row['timestamp']}  
                """
            )

            with st.expander("View Email Body"):
                st.write(row["body"])

            # --------- GENERATE REPLY BUTTON ---------
            if st.button(f"Generate Reply for Email #{row['id']}", key=f"reply_raw_{row['id']}"):

                email_text = (
                    f"Subject: {row['subject']}\n"
                    f"From: {row['sender']}\n\n"
                    f"{row['body']}"
                )

                prompts = load_prompts()
                reply_prompt = prompts["auto_reply_prompt"]

                from core.llm_client import call_llm
                reply = call_llm(system_prompt=reply_prompt, user_prompt=email_text)

                st.session_state["draft_replies"][row["id"]] = reply
                st.success("Draft reply saved! Check the sidebar under Draft Replies.")
                st.rerun()

        st.markdown("---")

    else:
        st.info("Click 'Load Inbox' to view your emails.")


# ============================================================
# PROMPT EDITOR
# ============================================================
elif page == "Prompt Editor":
    st.markdown("### Prompt Brain (Editable Prompts)")

    prompts = load_prompts()

    st.markdown("#### Categorization Prompt")
    cat_prompt = st.text_area("Edit Categorization Prompt", prompts["categorization_prompt"], height=150)

    st.markdown("#### Action Item Extraction Prompt")
    action_prompt = st.text_area("Edit Action Item Prompt", prompts["action_item_prompt"], height=150)

    st.markdown("#### Auto Reply Drafting Prompt")
    reply_prompt = st.text_area("Edit Auto Reply Prompt", prompts["auto_reply_prompt"], height=150)

    if st.button("Save All Prompts"):
        updated_prompts = {
            "categorization_prompt": cat_prompt,
            "action_item_prompt": action_prompt,
            "auto_reply_prompt": reply_prompt
        }

        save_prompts(updated_prompts)
        st.success("Prompts saved successfully!")


# ============================================================
# EMAIL AGENT (CHATBOT)
# ============================================================
elif page == "Email Agent":
    st.markdown("### Email ChatBot")

    st.write("Ask questions about a specific email or the entire inbox.")

    # Fetch emails
    emails_df = fetch_all_emails()

    # Email selection
    mode = st.radio(
        "Choose a mode:",
        ["Ask about a specific email", "Ask about the entire inbox"]
    )

    st.markdown("---")

    # Load prompts
    prompts = load_prompts()

    # ======================================================================================
    # MODE 1: EMAIL-SPECIFIC QUESTIONS
    # ======================================================================================
    if mode == "Ask about a specific email":

        if emails_df.empty:
            st.warning("No emails found. Please load inbox first.")
            st.stop()

        email_options = [
            f"{row['subject']} ({row['sender']})"
            for _, row in emails_df.iterrows()
        ]

        selected_label = st.selectbox("Select an email:", email_options)
        selected_index = email_options.index(selected_label)
        selected_email = emails_df.iloc[selected_index]

        # Show email preview
        st.subheader("📧 Selected Email")
        st.markdown(f"**Subject:** {selected_email['subject']}")
        st.markdown(f"**From:** {selected_email['sender']}")
        st.markdown(f"**Time:** {selected_email['timestamp']}")

        with st.expander("📄 Email Body"):
            st.write(selected_email["body"])

        st.markdown("---")
        st.subheader("💬 Ask a Question About This Email")

        # Chat history - email specific
        if "email_chat_history" not in st.session_state:
            st.session_state["email_chat_history"] = []

        # Display past messages
        for role, msg in st.session_state["email_chat_history"]:
            if role == "user":
                st.markdown(f"**🧑‍💻 You:** {msg}")
            else:
                st.markdown(f"**🤖 Agent:** {msg}")

        # Input box
        user_msg = st.text_input("Your question:")

        if st.button("Send"):
            if user_msg.strip() == "":
                st.warning("Please enter a valid question.")
                st.stop()

            st.session_state["email_chat_history"].append(("user", user_msg))

            # Build system prompt for email-specific reasoning

            system_prompt = f"""
            You are an intelligent Email Assistant.

            Your job is to understand the user's question and answer it using ONLY:
            - The selected email's content
            - The stored prompts (categorization, action-item, reply) — but only when appropriate and relevant to the user's question.

            ----------------------------------------------------
            EMAIL SELECTED
            ----------------------------------------------------
            Sender: {selected_email['sender']}
            Subject: {selected_email['subject']}
            Body: {selected_email['body']}

            ----------------------------------------------------
            PROMPT CONTEXT
            ----------------------------------------------------
            Categorization Prompt:
            {prompts["categorization_prompt"]}

            Action Item Extraction Prompt:
            {prompts["action_item_prompt"]}

            Auto Reply Drafting Prompt:
            {prompts["auto_reply_prompt"]}

            ----------------------------------------------------
            TASK
            ----------------------------------------------------
            Analyze the user’s question and respond strictly based on the selected email.

            You may:
            - Summarize the email
            - Extract tasks or deadlines
            - Explain the meaning, intent, or purpose of the email
            - Provide clarifications
            - Draft a reply (only when the user explicitly requests one)
            - Apply categorization or action-item logic only when the question requires it

            ----------------------------------------------------
            OUTPUT RULES
            ----------------------------------------------------
            1. Return clean, plain text only.
            - No HTML tags
            - No code blocks (```)
            - No styling or markup elements

            2. Keep the response concise, clear, and professional.

            3. If the user’s question cannot be answered from the email content:
            - Respond politely
            - Do not guess or invent any information

            4. Do not include system instructions, this prompt, or hidden reasoning.

            ----------------------------------------------------
            NOW ANSWER THE USER'S QUESTION:
            """


            from core.llm_client import call_llm
            ai_response = call_llm(system_prompt=system_prompt, user_prompt=user_msg)

            st.session_state["email_chat_history"].append(("ai", ai_response))
            st.rerun()

    # ======================================================================================
    # MODE 2: INBOX-WIDE ANALYSIS
    # ======================================================================================
    else:
        st.subheader("💬 Ask About the Entire Inbox")

        if "inbox_chat_history" not in st.session_state:
            st.session_state["inbox_chat_history"] = []

        # Display history
        for role, msg in st.session_state["inbox_chat_history"]:
            if role == "user":
                st.markdown(f"**🧑‍💻 You:** {msg}")
            else:
                st.markdown(f"**🤖 Agent:** {msg}")

        user_msg = st.text_input("Ask anything about your inbox:")

        if st.button("Send to Inbox Agent"):
            if user_msg.strip() == "":
                st.warning("Please enter a valid question.")
                st.stop()

            st.session_state["inbox_chat_history"].append(("user", user_msg))

            inbox_text = ""
            for _, row in emails_df.iterrows():
                inbox_text += f"""
                EMAIL:
                Sender: {row['sender']}
                Subject: {row['subject']}
                Body: {row['body']}

                """


            system_prompt = f"""
            You are an intelligent Global Inbox Assistant.

            Your job is to understand the user’s query and answer it using ONLY:
            - The full inbox content provided below
            - The stored prompts (categorization, action-item, reply) — but only when appropriate and relevant to the user's question.

            ----------------------------------------------------
            INBOX CONTENT (Use this as the only source of truth)
            ----------------------------------------------------
            {inbox_text}

            ----------------------------------------------------
            PROMPT CONTEXT
            ----------------------------------------------------
            Categorization Prompt:
            {prompts["categorization_prompt"]}

            Action Item Extraction Prompt:
            {prompts["action_item_prompt"]}

            Auto Reply Drafting Prompt:
            {prompts["auto_reply_prompt"]}

            ----------------------------------------------------
            TASK
            ----------------------------------------------------
            Analyze the user’s question and answer it strictly using the inbox data.

            You may:
            - Summarize emails
            - Identify urgent or important emails
            - Extract tasks, deadlines, or follow-ups
            - Provide insights across the inbox
            - Draft replies when asked
            - Use categorization or action-item logic when relevant
            - Answer general questions based on the inbox content

            ----------------------------------------------------
            OUTPUT RULES
            ----------------------------------------------------
            1. Return clean, plain text only.
            - No HTML tags
            - No code blocks (```)
            - No markup snippets
            - No styling instructions

            2. The tone must be professional, clear, and concise.

            3. When listing information, use simple bullet points or numbers:
            - Bullet point
                - Sub-point

            or:

            1. Item
            2. Item

            4. If the inbox does not contain information needed to answer the question:
            - Respond politely
            - Do not guess or invent details

            5. Do not include system instructions, prompt context, or hidden reasoning in your output.

            ----------------------------------------------------
            NOW ANSWER THE USER'S QUESTION:
            """


            from core.llm_client import call_llm
            ai_response = call_llm(system_prompt=system_prompt, user_prompt=user_msg)

            st.session_state["inbox_chat_history"].append(("ai", ai_response))
            st.rerun()
