import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class Config:
    """Configuration centralisée de l'application"""

    # Configuration Zammad
    ZAMMAD_API_URL = os.getenv("ZAMMAD_API_URL", "")
    ZAMMAD_API_TOKEN = os.getenv("ZAMMAD_API_TOKEN", "")

    # Configuration authentification webhook
    WEBHOOK_USERNAME = os.getenv("WEBHOOK_USERNAME", "")
    WEBHOOK_PASSWORD = os.getenv("WEBHOOK_PASSWORD", "")

    # Configuration Flask
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    PORT = int(os.getenv("FLASK_PORT", "5000"))

    # Configuration Mails (correction et paramètres SMTP)
    MAIL_FROM = os.getenv("MAIL_FROM", "")
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_RECIPIENTS = os.getenv("SMTP_RECIPIENTS", "").split(",")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True").lower() == "true"

    @classmethod
    def validate(cls):
        """Valide que toutes les configurations obligatoires sont présentes"""
        required_vars = [
            ("ZAMMAD_API_URL", cls.ZAMMAD_API_URL),
            ("ZAMMAD_API_TOKEN", cls.ZAMMAD_API_TOKEN),
            ("WEBHOOK_USERNAME", cls.WEBHOOK_USERNAME),
            ("WEBHOOK_PASSWORD", cls.WEBHOOK_PASSWORD),
            ("MAIL_FROM", cls.MAIL_FROM),
            ("SMTP_HOST", cls.SMTP_HOST),
            ("SMTP_PORT", cls.SMTP_PORT),
            ("SMTP_USERNAME", cls.SMTP_USERNAME),
            ("SMTP_PASSWORD", cls.SMTP_PASSWORD),
            ("SMTP_RECIPIENTS", cls.SMTP_RECIPIENTS),
        ]

        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)

        if missing_vars:
            raise ValueError(
                f"Variables d'environnement manquantes: {', '.join(missing_vars)}"
            )

        return True
