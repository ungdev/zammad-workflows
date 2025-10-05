import requests
from config import Config


class ZammadService:
    """Service pour interagir avec l'API Zammad"""

    def __init__(self):
        self.api_url = Config.ZAMMAD_API_URL
        self.api_token = Config.ZAMMAD_API_TOKEN
        self.headers = {
            "Authorization": f"Token token={self.api_token}",
            "Content-Type": "application/json",
        }

    def _create_article_with_attachment(
        self, ticket_id, subject, body, filename, pdf_base64
    ):
        """
        Crée un nouvel article dans un ticket avec une pièce jointe PDF

        Args:
            ticket_id (int): ID du ticket Zammad
            subject (str): Sujet de l'article
            body (str): Corps de l'article
            filename (str): Nom du fichier PDF
            pdf_base64 (str): Contenu PDF encodé en base64

        Returns:
            tuple: (success: bool, response_data: dict)
        """

        payload = {
            "ticket_id": ticket_id,
            "subject": subject,
            "body": body,
            "content_type": "text/plain",
            "attachments": [
                {
                    "filename": filename,
                    "data": pdf_base64,
                    "mime-type": "application/pdf",
                }
            ],
        }

        try:
            response = requests.post(
                f"{self.api_url}/ticket_articles",
                json=payload,
                headers=self.headers,
                timeout=30,
            )

            if response.status_code in [200, 201]:
                return True, {
                    "message": "PDF envoyé dans Zammad",
                    "response": response.json(),
                }
            else:
                return False, {
                    "error": response.text,
                    "status_code": response.status_code,
                }

        except requests.RequestException as e:
            return False, {"error": f"Erreur de connexion: {str(e)}"}

    def send_ticket_pdf(self, ticket_number, ticket_id, pdf_base64):
        """
        Méthode de convenance pour envoyer un PDF de ticket

        Args:
            ticket_number (str): Numéro du ticket
            ticket_id (int): ID du ticket
            pdf_base64 (str): PDF encodé en base64

        Returns:
            tuple: (success: bool, response_data: dict)
        """
        subject = f"PDF du ticket #{ticket_number}"
        body = "Voici le PDF généré automatiquement depuis le webhook."
        filename = f"ticket_{ticket_number}.pdf"

        return self._create_article_with_attachment(
            ticket_id, subject, body, filename, pdf_base64
        )

    def set_ticket_generation_false(self, ticket_id):
        payload = {"pdf_generation": "false"}

        try:
            response = requests.put(
                f"{self.api_url}/tickets/{ticket_id}",
                json=payload,
                headers=self.headers,
                timeout=30,
            )

            if response.status_code in [200, 201]:
                return True, {
                    "message": "Etat pdf_generation mis à jour dans Zammad",
                    "response": response.json(),
                }
            else:
                return False, {
                    "error": response.text,
                    "status_code": response.status_code,
                }

        except requests.RequestException as e:
            return False, {"error": f"Erreur de connexion: {str(e)}"}

    def get_article_by_id(self, article_id: int):

        try:
            response = requests.get(
                f"{self.api_url}/ticket_articles/{article_id}",
                headers=self.headers,
                timeout=30,
            )

            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": response.text,
                    "status_code": response.status_code,
                }

        except requests.RequestException as e:
            return {"error": f"Erreur de connexion: {str(e)}"}
