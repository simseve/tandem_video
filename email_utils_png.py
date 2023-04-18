import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from email.mime.image import MIMEImage

from PIL import Image

def send_email(sender_email, receiver_email, subject, link):
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
    message = MIMEMultipart("related")
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    # Convert the background image to base64
    with open("./tmp/thanks.png", "rb") as f:
        img_data = f.read()

    image = MIMEImage(img_data)
    image.add_header("Content-ID", "<background>")
    message.attach(image)

    # Create the HTML content with the background image
    html = f"""\
    <html>
    <head></head>
    <body style="background-image: url('cid:background');">
    <p>To download the video, click <a href="{link}" download>here</a>.</p>

    </body>
    </html>
    """

    html_part = MIMEText(html, "html")
    message.attach(html_part)    # Send the email

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
    subject = 'Grazie per aver volato con Simone '
    link="http://www.corriere.it"

    send_email(sender_email, receiver_email, subject, link)
