# 🧠 Mistral Doc RAG

Un projet full-stack avec un **frontend React** et un **backend Python**, déployé via Docker.  
Ce projet permet d’interroger la documentation Mistral à travers une interface web conversationnelle.

## 📁 Structure du projet

```bash
mistral_doc_rag/
├── backend/      # Backend FastAPI (Python)
├── frontend/     # Frontend React (Vite)
├── docker-compose.yml
```

---

## 🚀 Lancer l'application

Assurez-vous d’avoir [Docker](https://www.docker.com/products/docker-desktop) installé.

### 🔧 1. Cloner le projet

```bash
git clone https://github.com/Farfire/mistral_doc_rag.git
cd mistral_doc_rag
```

### 📦 2. Lancer les services

```bash
docker compose up --build
```

Cela démarre :
- 🎯 `backend` sur [http://localhost:8000](http://localhost:8000)
- 💬 `frontend` sur [http://localhost:5173](http://localhost:5173)

---

## ⚙️ Configuration

Créez un fichier `.env` dans le dossier `backend/` :

```env
OPENAI_API_KEY=...
```

---

## 🛠️ Technologies utilisées

- ⚙️ **Backend** : Python, FastAPI, FAISS, Uvicorn
- 💻 **Frontend** : React, Vite, Chakra UI
- 🐳 **Containerisation** : Docker, Docker Compose

---

