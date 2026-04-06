"""
SendGrid Email Backend for Django
Sends emails using SendGrid API instead of SMTP (works better on Render free tier)
"""
import os
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage, EmailMultiAlternatives
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment
import logging

logger = logging.getLogger(__name__)


class SendGridBackend(BaseEmailBackend):
    """
    Django email backend using SendGrid API
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = os.getenv('SENDGRID_API_KEY')
        if not self.api_key:
            logger.error("SENDGRID_API_KEY not found in environment variables")

    def send_messages(self, email_messages):
        """
        Send a list of email messages
        """
        if not self.api_key:
            if not self.fail_silently:
                raise ValueError("SENDGRID_API_KEY not configured")
            return 0

        sent_count = 0
        for email_message in email_messages:
            try:
                self._send_message(email_message)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send email via SendGrid: {e}")
                if not self.fail_silently:
                    raise

        return sent_count

    def _send_message(self, email_message):
        """
        Send a single email message via SendGrid
        """
        from_email = Email(email_message.from_email)
        to_emails = [Email(to) for to in email_message.to]

        # Create the email content
        subject = email_message.subject

        # Handle HTML and plain text versions
        html_content = None
        text_content = None

        if isinstance(email_message, EmailMultiAlternatives):
            for alt in email_message.alternatives:
                if alt[1] == 'text/html':
                    html_content = alt[0]
                elif alt[1] == 'text/plain':
                    text_content = alt[0]

        # If no alternatives, use the body
        if not html_content and not text_content:
            text_content = email_message.body

        # Create SendGrid mail object
        mail = Mail(from_email, to_emails[0], subject)

        if html_content:
            mail.content = Content("text/html", html_content)
        elif text_content:
            mail.content = Content("text/plain", text_content)

        # Add CC recipients
        if email_message.cc:
            for cc_email in email_message.cc:
                mail.add_cc(Email(cc_email))

        # Add BCC recipients
        if email_message.bcc:
            for bcc_email in email_message.bcc:
                mail.add_bcc(Email(bcc_email))

        # Send via SendGrid API
        sg = SendGridAPIClient(self.api_key)
        response = sg.send(mail)

        # Log response
        logger.info(f"SendGrid response: {response.status_code}")

        if response.status_code not in [200, 201, 202]:
            raise Exception(f"SendGrid API error: {response.status_code} - {response.body}")
