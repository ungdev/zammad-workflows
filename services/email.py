import smtplib
from email.mime.base import MIMEBase  # pylint: disable=import-error,no-name-in-module
from email.mime.multipart import (  # pylint: disable=import-error,no-name-in-module
    MIMEMultipart,
)
from email.mime.text import MIMEText  # pylint: disable=import-error,no-name-in-module
from email import encoders  # pylint: disable=import-self

from config import Config


class EmailService:
    def __init__(self):
        self.smtp_host = Config.SMTP_HOST
        self.smtp_port = Config.SMTP_PORT
        self.username = Config.SMTP_USERNAME
        self.password = Config.SMTP_PASSWORD
        self.use_tls = Config.SMTP_USE_TLS
        self.recipients = Config.SMTP_RECIPIENTS

    def send_email_with_pdf(
        self,
        pdf_bytes: bytes,
        filename: str = "document.pdf",
    ):
        message = MIMEMultipart()
        message["From"] = self.username
        message["To"] = ", ".join(self.recipients)
        message["Subject"] = "Notification d'Evenement Automatique"

        body = "Vous trouverez en pièce jointe le document PDF généré automatiquement."
        message.attach(MIMEText(body, "plain"))

        part = MIMEBase("application", "pdf")
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        message.attach(part)

        if self.use_tls:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(
                    self.username,
                    Config.SMTP_RECIPIENTS,
                    message.as_string(),
                )
        else:
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.username, self.password)
                server.sendmail(
                    self.username,
                    Config.SMTP_RECIPIENTS,
                    message.as_string(),
                )
