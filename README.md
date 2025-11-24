# Smart-Email-Assistant
A Streamlit-based AI system for intelligent email processing, task extraction, and inbox reasoning.

## 1. Overview
The Smart Email Productivity Assistant is an AI-powered web application that streamlines email management using LLMs.
It processes emails, categorizes them, extracts actionable tasks, drafts responses, and enables conversational interaction with emails through an intelligent chatbot.

Built with Streamlit, SQLite, and Gemini API, this application simulates a real-world productivity agent with modular components for UI, backend, database, and prompting logic.

#### Experience the fully deployed Smart Email Assistant here 👉 : https://smart-email-assistant-nr.streamlit.app/

## 2. Key Features
### 2.1 Automated Email Categorization
Classifies emails into categories such as:
- To-Do
- Newsletter
- Reminder
- Project Update
- Finance
- Important
- General Inquiry
- Spam/Promotions

### 2.2 Action Item Extraction
Identifies: 
- Tasks
- Deadlines
- Required follow-ups

### 2.3 AI-Generated Reply Drafts
- Click Generate Reply for any email to produce a clean, well-written draft stored in the sidebar.

### 2.4 Intelligent Email Chatbot
Two modes of interaction:
- Specific Email Mode – ask questions about one email
- Global Inbox Mode – ask cross-inbox questions such as:
  - “Show me urgent emails”
  - “Summaries of all deadlines”
  - “Which emails require follow-up?”

### 2.5 Editable Prompt Engine
Modify the categorization prompt, task extraction prompt, and reply drafting prompt directly from the UI.

## 3. 📂 Project Structure
```smart-email-assistant/
│── app.py
│── requirements.txt
│── README.md
│
│── core/
│   ├── llm_client.py
│   ├── processor.py
│   ├── prompts.py
│
│── database/
│   ├── db.py
│   ├── emails.db
    ├── setup_db.py
│
│── assets/
│   ├── prompts.json
```

## 4. Installation & Setup
### 4.1 Clone the Repository
<pre>git clone https://github.com/nathania-rachael/smart-email-assistant.git
cd smart-email-assistant
</pre>

### 4.2 Create Virtual Environment (optional)
```python -m venv venv
source venv/bin/activate           # Mac/Linux
venv\Scripts\activate              # Windows
```

### 4.3 Install Dependencies
```
pip install -r requirements.txt
```

### 4.4 API Key Configuration
This application uses Streamlit Secrets for securely storing the Gemini API key.
#### (a) Local Development
- Create a folder named:
```
.streamlit/
```

- Inside it, create a file:
```
.streamlit/secrets.toml
```

- Add:
```
API_KEY = "your-gemini-api-key"
```

#### (b) Deployment on Streamlit Cloud
- Go to Settings -> Secrets
- Add:
```
API_KEY = "your-gemini-api-key"
```

## 5. Running the Application 
Start Streamlit
```
streamlit run app.py
```
## Phase 1: Using the Mock Inbox
- Navigate to View & Process Mails
- Click Load Inbox
- Click Process Inbox with AI
    - Emails will be categorized
    - Tasks will be extracted
    - Results stored in SQLite
You can now browse each email with its associated metadata and tasks.

## Phase 2: Managing Prompts
Go to Prompt Editor to update:
- Categorization Prompt
- Task Extraction Prompt
- Auto Reply Drafting Prompt
Click Save Prompts so that the updated prompts are used.
Prompts are stored in assets/prompts.json and loaded dynamically.

## Phase 3: Email Chat Agent
### (a) Specific Email Mode: 
Ask questions like:
   - "Summarize this email”
   - “What tasks do I need to complete?”
   - “Explain what the sender is asking”
### (b) Global Email Mode: 
Ask broader queries such as:
   - "Show all pending tasks”
   - “List emails with deadlines”
   - “Which emails are urgent?”
   - “Give summaries of all reminders”
The agent uses your prompts + inbox content + user message to generate structured answers.

## Database
The project uses a local SQLite database (emails.db) with fields:
- id
- sender
- subject
- timestamp
- body
- category (category is stored here once processed with AI)
- action_items (action items are stored here once processed with AI)
- processed
You can update or replace the database as needed.

## Conclusion
The Smart Email Productivity Assistant demonstrates:
- Effective prompt engineering
- Modular LLM-based design
- Clean Streamlit UI development
- Practical use of SQLite for mock data
- Real-world application of AI-driven email processing
