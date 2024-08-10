import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from server.app.core.config import settings


def send_reset_password_email(email: str, token: str) -> str:
    # TURNED OFF FOR NOW, TODO: TEST
    return "Email sending is turned off"

    # Define the email subject and body
    # subject = "Password Reset Request"
    # reset_link = f"https://your-app.com/reset-password?token={token}"  # Adjust to your actual URL
    # body = f"""
    # Hi,
    #
    # You have requested to reset your password. Please click the link below to reset your password:
    #
    # {reset_link}
    #
    # If you did not request this change, please ignore this email.
    #
    # Best regards,
    # NexusWare WMS Team
    # """
    #
    # # Create the MIMEText object to represent the email
    # message = MIMEMultipart()
    # message['From'] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
    # message['To'] = email
    # message['Subject'] = subject
    #
    # # Attach the email body to the email
    # message.attach(MIMEText(body, 'plain'))
    #
    # try:
    #     # Connect to the SMTP server and send the email
    #     server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
    #     server.starttls()
    #     server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
    #     server.sendmail(settings.EMAIL_FROM, email, message.as_string())
    #     server.close()
    #     return "Email sent successfully"
    # except Exception as e:
    #     return f"Failed to send email: {str(e)}"
