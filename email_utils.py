import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

def send_email(sender_email, receiver_email, subject, body, attachment_path=None):
    """
    Send an email with or without an attachment.
    
    Args:
    sender_email (str): The sender's email address.
    receiver_email (str): The recipient's email address.
    subject (str): The subject line of the email.
    body (str): The body text of the email.
    attachment_path (str): (optional) The file path of an attachment to include in the email.
    
    Returns:
    None
    """
    # Load environment variables from .env file
    load_dotenv()

    # Set up the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # Add an attachment (optional)
    if attachment_path:
        filename = attachment_path.split('/')[-1]
        attachment = open(attachment_path, 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {filename}")
        message.attach(part)

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, os.getenv('GMAIL_PASSWORD'))
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        print(f"Email sent to '{receiver_email}' successfully.")
    except Exception as e:
        print(f"Error sending email: {str(e)}")
    finally:
        server.quit()

if __name__ == '__main__':
    sender_email = 'severini.simone@gmail.com'
    receiver_email = 'severini.simone@icloud.com'
    subject = 'Test email'
    body = f'Carissimo/a,\n\ngrazie per aver condividiso con me questo bellissimo volo. Questo il link dove scaricarlo http://www.seve-ai.com'

    send_email(sender_email, receiver_email, subject, body)