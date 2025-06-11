# Backend API Documentation

Ce backend expose une API FastAPI pour interagir avec Mistral AI et l'API météo Google.

## Endpoints

- **GET /**  
  Retourne un message de bienvenue et la documentation.

- **POST /api/chat**  
  Envoie un message à Mistral AI et retourne la réponse.  
  **Body:**

  ```json
  {
    "message": "Votre message",
    "model": "mistral-large-latest"
  }
  ```

- **GET /api/models**  
  Retourne la liste des modèles Mistral disponibles.

- **POST /api/reset**  
  Réinitialise l'historique de conversation.

- **GET /api/weather**  
  Retourne les conditions météo actuelles pour une latitude et longitude données.  
  **Query Parameters:**
  - `latitude`: Latitude du lieu (float)
  - `longitude`: Longitude du lieu (float)

## Variables d'environnement

Le backend nécessite les variables d'environnement suivantes :

- `MISTRAL_API_KEY`: Clé API Mistral
- `GOOGLE_API_KEY`: Clé API Google pour l'API météo

Ces variables doivent être définies dans un fichier `.env` à la racine du dossier backend.

## Lancement du serveur

Pour lancer le serveur, exécutez la commande suivante depuis le dossier backend :

```bash
uvicorn app.main:app --reload
```

Le serveur sera accessible à l'adresse `http://localhost:8000`.
