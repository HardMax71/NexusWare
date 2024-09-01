import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


def send_reset_password_email(email: str, token: str) -> str:
    # TURNED OFF FOR NOW
    return "Email sending is turned off"

    # Define the email subject and body
    subject = "Password Reset Request"
    reset_link = f"{settings.PASSWORD_RESET_LINK}?token={token}"

    # HTML body with some basic styling
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #4a4a4a;">Password Reset Request</h2>
            <p>Hi,</p>
            <p>You have requested to reset your password. Please click the button below to reset your password:</p>
            <p>
                <a href="{reset_link}" style="display: inline-block; padding: 10px 20px; 
                background-color: #007bff; color: #ffffff; text-decoration: none; border-radius: 5px;">
                    Reset Password
                </a>
            </p>
            <p>If you did not request this change, please ignore this email.</p>
            <p>
                Best regards,<br>
                NexusWare WMS Team
            </p>
        </body>
    </html>
    """

    message = MIMEMultipart('alternative')
    message['From'] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
    message['To'] = email
    message['Subject'] = subject

    # Attach both plain text and HTML versions
    text_part = MIMEText(f"Please reset your password by visiting: {reset_link}", 'plain')
    html_part = MIMEText(html_body, 'html')

    message.attach(text_part)
    message.attach(html_part)

    try:
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, email, message.as_string())
        server.close()
        return "Email sent successfully"
    except Exception as e:
        return f"Failed to send email: {str(e)}"
