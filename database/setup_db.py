import sqlite3

def setup_database():
    conn = sqlite3.connect("emails.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            subject TEXT,
            timestamp TEXT,
            body TEXT,
            category TEXT
        )
    """)

    # Clear existing records
    cursor.execute("DELETE FROM emails")

    sample_emails = [
        ("product.manager@acmecorp.com",
         "Meeting Request: Sprint Planning for Release v3.2",
         "2025-11-18T09:15:00",
         "Hi team, we need to schedule our sprint planning for Release v3.2. "
         "Please confirm your availability for a 30-minute sync tomorrow at 2:00 PM.",
         None),

        ("newsletter@techinsights.io",
         "Tech Insights Weekly – AI Breakthroughs, Cloud Trends",
         "2025-11-17T07:30:00",
         "Welcome to this week's edition of Tech Insights! In this issue, we cover recent "
         "advancements in generative AI, cloud security updates, and automation trends.",
         None),

        ("offers@rewardhub.co",
         "Exclusive Offer: Get ₹2000 Cashback – Limited Time",
         "2025-11-16T10:10:00",
         "Congratulations! You are eligible for a special cashback reward. Click the link "
         "below to claim your offer. Hurry, this is valid for the next 24 hours!",
         None),

        ("alpha.teamlead@acmecorp.com",
         "Project Alpha – Weekly Status Update",
         "2025-11-15T14:00:00",
         "Hi, here is the latest update for Project Alpha. The authentication module has been "
         "integrated successfully. Please review the updated API documentation.",
         None),

        ("hr.operations@acmecorp.com",
         "Action Required: Submit PAN & Aadhar Verification Documents",
         "2025-11-14T12:25:00",
         "Dear employee, this is a reminder to submit your PAN and Aadhar verification "
         "documents by Friday EOD to complete your onboarding formalities.",
         None),

        ("client.relations@globexsolutions.com",
         "Follow-Up: Clarification Needed on Latest Proposal",
         "2025-11-13T11:05:00",
         "Hello, we wanted to confirm whether you had the chance to review the proposal we "
         "sent last week. Please share any clarifications or feedback.",
         None),

        ("accounts.billing@acmecorp.com",
         "Invoice #AC-9823 for October 2025",
         "2025-11-12T09:45:00",
         "Dear customer, please find attached the invoice for the month of October (Invoice No. AC-9823). "
         "Kindly process the payment before November 20th.",
         None),

        ("admin.office@university.edu",
         "Reminder: Course Registration Closes Tomorrow",
         "2025-11-11T17:00:00",
         "This is to remind you that course registration for the upcoming semester closes "
         "tomorrow at 5:00 PM. Ensure you complete the registration to avoid late fees.",
         None),

        ("support@cloudservice.io",
         "Update on Your Support Ticket #48291",
         "2025-11-10T15:20:00",
         "We investigated your reported issue and have deployed a fix to production. "
         "Please check and confirm if everything works as expected.",
         None),

        ("student.council@university.edu",
         "Query: Project Submission Format Clarification",
         "2025-11-09T16:40:00",
         "Hi, could you please clarify the formatting rules required for uploading the final project? "
         "Should it be a PDF along with the source code, or only the report?",
         None)
    ]

    cursor.executemany("""
        INSERT INTO emails (sender, subject, timestamp, body, category)
        VALUES (?, ?, ?, ?, ?)
    """, sample_emails)

    conn.commit()
    conn.close()
    print("Database setup complete. New sample emails added.")

if __name__ == "__main__":
    setup_database()
