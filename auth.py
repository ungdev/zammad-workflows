from flask import request, jsonify
from functools import wraps
from config import Config


def check_auth(username, password):
    """Vérifie les identifiants d'authentification"""
    return username == Config.WEBHOOK_USERNAME and password == Config.WEBHOOK_PASSWORD


def authenticate():
    """Renvoie une réponse 401 demandant l'authentification"""
    return jsonify({"error": "Authentication required"}), 401


def requires_auth(f):
    """Décorateur pour vérifier l'authentification HTTP Basic"""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated
