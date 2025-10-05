# Zammad Workflows

Webhook Flask pour générer automatiquement des PDFs à partir des tickets Zammad du BDE.

## Structure du projet

```
bde-tickets-to-pdf/
├── server.py                      # Point d'entrée Flask (endpoints, auth)
├── wsgi.py                        # Entrée WSGI (exporte `application`) pour gunicorn/uWSGI
├── config.py                      # Chargement/validation des variables d'environnement
├── auth.py                        # Décorateur @requires_auth pour le webhook
├── services/
│   ├── pdf.py                     # Génération des PDFs (ReportLab)
│   ├── zammad.py                  # Interaction avec l'API Zammad
│   └── email.py                   # Envoi d'emails avec pièce jointe PDF (SMTP)
├── requirements.txt               # Dépendances Python
├── docker-compose.yaml            # Exemple de configuration Docker Compose
├── .env.example                   # Exemple de variables d'environnement
└── README.md                      # Documentation (ce fichier)
```

## Configuration

1. Copiez `.env.example` vers `.env` :
   ```bash
   cp .env.example .env
   ```

2. Modifiez le fichier `.env` avec vos valeurs :
   ```env
   ZAMMAD_API_URL=https://votre-instance.zammad.com/api/v1/ticket_articles
   ZAMMAD_API_TOKEN=votre_token_api_zammad
   WEBHOOK_USERNAME=votre_nom_utilisateur
   WEBHOOK_PASSWORD=votre_mot_de_passe_securise
   FLASK_DEBUG=false
   FLASK_PORT=5000
   SMTP_HOST=smtp.example.com
   SMTP_PORT=587
   SMTP_USERNAME=...
   SMTP_PASSWORD=...
   MAIL_FROM=webhook@example.com
   ```

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
python server.py
```

Le serveur démarre sur `http://localhost:5000` (ou le port configuré).

### En production (WSGI)

Ne pas utiliser le serveur de développement Flask en production. Utilisez un serveur WSGI comme gunicorn ou waitress.

Exemple avec gunicorn :

```bash
# depuis le répertoire du projet
pip install gunicorn
# lancer 4 workers et écouter sur le port 8080
gunicorn --workers 4 --bind 0.0.0.0:8080 wsgi:application
```

Exemple avec waitress (Windows / simplicité) :

```bash
pip install waitress
python -m waitress --port=8080 wsgi:application
```

Remarques :
- Assurez-vous que FLASK_DEBUG=false dans vos variables d'environnement pour la production.
- Vérifiez la configuration des variables d'environnement (voir .env.example) avant de démarrer.
- Pour déploiements robustes, utilisez un process manager (systemd, supervisor) et configurez la rotation des logs et la supervision.

## Endpoint

- **POST** `/webhook` - Reçoit les données de ticket Zammad et génère un PDF

### Authentification

L'endpoint nécessite une authentification HTTP Basic avec les identifiants configurés dans le fichier `.env`.

### Exemple de requête

Le webhook attend un JSON avec la structure :
```json
{
  "ticket": {
    "id": 123,
    "number": "32087",
    "title": "Titre du ticket",
    "owner": {
      "firstname": "Jean",
      "lastname": "Dupont"
    },
    // ... autres champs BDE
  },
  "article": {
    "body": "Contenu de l'article",
    "from": "user@example.com",
    "created_at": "2025-09-25T10:30:00Z"
  }
}
```