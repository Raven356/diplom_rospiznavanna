from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import requests
import cv2
import threading
import time
import constants

class MailProvider:
    def send_email(self, subject, body, image, callback):
    # Email configurations
        sender_email = constants.sender_email
        receiver_email = constants.receiver_email
        api_key = constants.api_key
        domain = constants.domain

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email

        # Attach text body
        text = MIMEText(body)
        msg.attach(text)

        # Attach image
        img_content = cv2.imencode('.jpg', image)[1].tostring()
        img = MIMEImage(img_content)
        msg.attach(img)

        # Send the message via Mailgun SMTP server
        def send_message():
            mailgun_url = f"https://api.mailgun.net/v3/{domain}/messages"
            response = requests.post(
                mailgun_url,
                auth=("api", api_key),
                files=[("attachment", img_content)],
                data={"from": sender_email,
                    "to": receiver_email,
                    "subject": subject,
                    "text": body})
            if response.status_code != 200:
                print("Failed to send email:", response.text)
            
            callback(time.time(), 0)

        email_thread = threading.Thread(target=send_message)
        email_thread.start()  