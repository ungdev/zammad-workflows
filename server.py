from flask import Flask, request, jsonify
from config import Config
from auth import requires_auth
from services.pdf import PDFGenerator
from services.zammad import ZammadService
from services.email import EmailService
import threading

try:
    Config.validate()
except ValueError as e:
    print(f"Erreur de configuration: {e}")
    exit(1)

app = Flask(__name__)

zammad_service = ZammadService()
email_service = EmailService()


@app.route("/webhook", methods=["POST"])
@requires_auth
def webhook():
    """Endpoint webhook pour traiter les données Zammad et générer un PDF"""
    data: dict | None = request.get_json()
    if not data:
        return jsonify({"error": "No JSON received"}), 400

    ticket = data.get("ticket", {})

    ticket_id = ticket.get("id")
    ticket_number = ticket.get("number", "N/A")

    pdf_generation_value = ticket.get("pdf_generation", "false")

    if not ticket_id:
        return jsonify({"error": "ticket_id manquant"}), 400

    def background_job(ticket, ticket_number, ticket_id):
        try:
            if not pdf_generation_value == "false":

                zammad_service.set_ticket_generation_false(ticket_id)

                pdf_generator = PDFGenerator()

                pdf_generator.generate_ticket_pdf(ticket, zammad_service)

                success_z, response_z = zammad_service.send_ticket_pdf(
                    ticket_number, ticket_id, pdf_generator.pdf_base64
                )
                if not success_z:
                    print(
                        f"[background] Erreur Zammad pour ticket {ticket_number}: {response_z}"
                    )

                if pdf_generation_value == "email":
                    email_service.send_email_with_pdf(
                        pdf_generator.pdf_bytes,
                        filename=f"ticket_{ticket_number}.pdf",
                    )

        except Exception as e:
            print(f"[background] Erreur traitement ticket {ticket_number}: {e}")

    thread = threading.Thread(
        target=background_job,
        args=(ticket, ticket_number, ticket_id),
        daemon=True,
    )
    thread.start()

    return (
        jsonify(
            {"status": "accepted", "message": "Traitement démarré en arrière-plan"}
        ),
        202,
    )


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=Config.PORT)
