import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def send_email(sender_user, sender_pass, recipient, html_content):
    """
    Send an HTML email report to the specified recipient.

    Args:
        sender_user (str): Gmail username (email).
        sender_pass (str): Gmail app password.
        recipient (str): Target email address.
        html_content (str): HTML body to send.

    Returns:
        str: Success or error message for logging/debugging.
    """
    try:
        print(f"📧 Sending email to: {recipient}...")

        msg = MIMEMultipart("alternative")
        msg["From"] = sender_user
        msg["To"] = recipient
        msg["Subject"] = f"🚀 Business Briefing: {datetime.now().strftime('%Y-%m-%d')}"

        msg.attach(MIMEText(html_content, "html"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_user, sender_pass)

        server.sendmail(sender_user, recipient, msg.as_string())
        server.quit()

        print("✅ Email sent successfully!")
        return "✅ Email sent successfully!"

    except Exception as e:
        error_msg = f"❌ Email Error: {e}"
        print(error_msg)
        return error_msg