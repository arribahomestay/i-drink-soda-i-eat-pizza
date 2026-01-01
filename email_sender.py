import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

def send_email_with_attachment(settings, file_path, subject, body):
    """
    Send email with attachment using SMTP
    settings: tuple from database (id, sender, password, receiver, server, port, updated_at)
    """
    if not settings:
        return False, "No email settings configured."
    
    # Unpack settings
    sender_email = settings[1]
    sender_password = settings[2]
    receiver_email = settings[3]
    smtp_server = settings[4]
    smtp_port = settings[5]
    
    if not sender_email or not sender_password or not receiver_email:
        return False, "Incomplete email configuration. Please check Settings > Email."
        
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attachment
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            msg.attach(part)
        except Exception as e:
            return False, f"Error attaching file: {str(e)}"
    
    # Send
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True, "Email sent successfully!"
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed. Check your email and App Password."
    except Exception as e:
        return False, f"Sending failed: {str(e)}"
