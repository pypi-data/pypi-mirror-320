import requests

class EtidelPython:
    def __init__(self, api_url, api_key):
        """
        Initialise l'instance du service d'envoi de SMS.
        
        :param api_url: URL de l'API d'envoi de SMS.
        :param api_key: Clé API pour authentification.
        """
        self.api_url = api_url
        self.api_key = api_key

    def send_sms(self, to, message):
        """
        Envoie un SMS à un destinataire.

        :param to: Numéro de téléphone du destinataire (format international).
        :param message: Contenu du SMS.
        :return: Réponse de l'API.
        """
        payload = {
            "to": to,
            "message": message,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()  # Génère une exception si l'API retourne une erreur HTTP
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
