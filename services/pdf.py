import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from services.zammad import ZammadService


class PDFGenerator:
    """Générateur de PDF pour les tickets Zammad"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.pdf_bytes: bytes = None
        self.pdf_base64: str = None

    def _format_value(self, value: str | bool | int) -> str:
        """Formate une valeur pour l'affichage dans le PDF"""
        if value is None or value == "":
            return "Non défini"
        elif value is False:
            return "Non"
        elif value is True:
            return "Oui"
        elif isinstance(value, str) and value.endswith(":00:00.000Z"):
            return self._format_date(value)
        return str(value)

    def _clean_html(self, html_content: str) -> str:
        """Nettoie le contenu HTML simple"""
        return (
            html_content.replace("<br>", "\n")
            .replace("<div>", "")
            .replace("</div>", "\n")
        )

    def _close_br_tag_html(self, html_content):
        """Ferme les tags HTML <br>"""
        return html_content.replace("<br>", "<br></br>")

    def _format_date(self, date_str: str) -> str:
        """Formate une date ISO en format lisible"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                "%d/%m/%Y %H:%M"
            )
        except (TypeError, ValueError):
            return date_str

    def _create_bde_table(self, ticket):
        """Crée le tableau des informations BDE Club/Asso"""
        table_data = [["Champ", "Valeur"]]

        # Champs spécifiques du BDE
        bde_fields = [
            ("Date de début", "date_begin"),
            ("Date de fin", "date_end"),
            ("Nombre de participants attendus", "bde_clubasso_participants_nb"),
            ("Présence de public extérieur", "bde_clubasso_externals"),
            ("Lieux", "places"),
            ("Boissons & Nourriture", "bde_clubasso_food"),
            ("Nom/Prénom des responsables", "bde_clubasso_orgas"),
            ("Evènement hebdomadaire", "bde_com_hebdo"),
        ]

        for display_name, field_key in bde_fields:
            value = self._format_value(ticket.get(field_key))
            table_data.append([display_name, value])

        table = Table(table_data, colWidths=[200, 300])
        table.setStyle(
            TableStyle(
                [
                    # En-tête avec fond bleu et texte blanc
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976D2")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 13),
                    # Contenu avec alternance de lignes
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F5F7FA")),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.HexColor("#F5F7FA"), colors.HexColor("#E3E8EE")],
                    ),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 11),
                    # Bordures fines et arrondies
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B0BEC5")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#1976D2")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        return table

    def generate_ticket_pdf(self, ticket: dict, zammad_instance: ZammadService):
        """
        Génère un PDF à partir des données de ticket et d'article

        Args:
            ticket (dict): Données du ticket Zammad
            article (dict): Données de l'article Zammad

        Returns:
            str: PDF encodé en base64
        """

        ticket_number: str = ticket.get("number", "N/A")
        ticket_title: str = ticket.get("title", "N/A")

        owner: dict = ticket.get("owner", {})
        ticket_owner: str = (
            f"{owner.get('firstname', 'N/A')} {owner.get('lastname', '')}"
        )

        ticket_created_by: dict = ticket.get("created_by", {})
        ticket_created_by_str: str = (
            f"{self._format_value(ticket_created_by.get('firstname'))} "
            f"{self._format_value(ticket_created_by.get('lastname'))}"
        )
        ticket_created_at_raw = self._format_value(ticket.get("created_at"))
        ticket_created_at = self._format_date(ticket_created_at_raw)
        ticket_club_name = self._format_value(ticket.get("bde_log_clubasso_name"))

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        elements.append(
            Paragraph(f"Ticket #{ticket_number}: {ticket_title}", self.styles["Title"])
        )
        elements.append(Spacer(1, 6))
        elements.append(
            Paragraph(f"Club/Asso: {ticket_club_name}", self.styles["Heading2"])
        )
        elements.append(Spacer(1, 6))
        elements.append(
            Paragraph(f"Demande de: {ticket_created_by_str}", self.styles["Normal"])
        )
        elements.append(
            Paragraph(f"Responsable BDE: {ticket_owner}", self.styles["Normal"])
        )

        elements.append(
            Paragraph(f"Envoyée le: {ticket_created_at}", self.styles["Normal"])
        )
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Informations Evènement", self.styles["Heading2"]))
        elements.append(Spacer(1, 6))
        elements.append(self._create_bde_table(ticket))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Description", self.styles["Heading2"]))
        elements.append(Spacer(1, 6))

        article_ids = ticket.get("article_ids", [])
        articles_data = []
        for article_id in article_ids:
            article_data = zammad_instance.get_article_by_id(article_id)
            if article_data:
                articles_data.append(
                    {
                        "created_at": article_data.get("created_at", ""),
                        "body": article_data.get("body", ""),
                        "from": article_data.get("from", "N/A"),
                        "type_id": article_data.get("type_id", 0),
                    }
                )
        articles_data.sort(key=lambda x: x.get("created_at", ""))

        description_body = self._close_br_tag_html(
            articles_data[0].get("body", "") if articles_data else ""
        )
        elements.append(Paragraph(description_body, self.styles["Normal"]))

        elements.append(Paragraph("Messages", self.styles["Heading2"]))

        for article_data in articles_data[1:]:
            if article_data.get("type_id", 0) == 10:
                sender = article_data.get("from", "N/A")
                body = self._close_br_tag_html(
                    article_data.get("body", "") if articles_data else ""
                )
                created_at = ticket_created_at = datetime.strptime(
                    article_data.get("created_at", ""), "%Y-%m-%dT%H:%M:%S.%fZ"
                ).strftime("%d/%m/%Y %H:%M")
                elements.append(Paragraph(body, self.styles["BodyText"]))
                elements.append(
                    Paragraph(
                        sender,
                        bulletText=None,
                        style=self.styles["Normal"].clone("right", alignment=2),
                    )
                )
                elements.append(
                    Paragraph(
                        created_at,
                        bulletText=None,
                        style=self.styles["Normal"].clone("right", alignment=2),
                    )
                )
                elements.append(Spacer(1, 12))

        doc.build(elements)
        buffer.seek(0)

        self.pdf_bytes = buffer.getvalue()
        self.pdf_base64 = base64.b64encode(self.pdf_bytes).decode("utf-8")
