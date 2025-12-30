import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_chunk_email(to_email, subject, html_content):
    """
    Sends an HTML email using Gmail SMTP.
    """
    gmail_user = os.getenv('GMAIL_USER')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    
    if not gmail_user or not gmail_password:
        raise ValueError("GMAIL_USER and GMAIL_APP_PASSWORD must be set in .env file")

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = gmail_user
    
    # Handle multiple recipients
    if isinstance(to_email, str):
        if ';' in to_email:
            recipients = [e.strip() for e in to_email.split(';')]
        elif ',' in to_email:
            recipients = [e.strip() for e in to_email.split(',')]
        else:
            recipients = [to_email]
    else:
        recipients = to_email
        
    msg['To'] = ", ".join(recipients)

    # Attach HTML content
    part = MIMEText(html_content, 'html')
    msg.attach(part)

    try:
        # Connect to Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_password)
        
        server.sendmail(gmail_user, recipients, msg.as_string())
        server.close()
        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise e
