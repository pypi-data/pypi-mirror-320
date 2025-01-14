def greet():
    return f"Hey doov whats up?"

import smtplib
from email.mime.text import MIMEText

def daily_reflection():
    # Prompt for user name
    name = input("Please enter your name: ")

    # Questions
    questions = [
        "3 things I did for myself:",
        "3 reasons I’m grateful for Prateek/Divya today:",
        "What went well in my day:",
        "What can I improve on:",
        "1 manifestation:"
    ]

    # Collect answers
    answers = {}
    for question in questions:
        print(question)
        answers[question] = input("Your answer: ")

    # Display collected answers
    print("\nHere are your responses:")
    for question, answer in answers.items():
        print(f"{question} {answer}")

    # Email setup
    recipient_email = input("Enter the recipient's email address: ")
    sender_email = "spogtrop@gmail.com"  # Replace with your email
    sender_password = "cjba tgtr vkqb cyoq"  # Replace with your email password

    subject = f"Daily Reflection by {name}"
    body = "\n\n".join([f"{q}\n{a}" for q, a in answers.items()])

    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Bcc'] = sender_email

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
