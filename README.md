# YouTube Uploader Bot 🎥🤖

Une application Python avec interface graphique (Tkinter) permettant d’uploader automatiquement plusieurs vidéos sur YouTube à partir de différents comptes.

## 🚀 Fonctionnalités principales
- Upload automatique de vidéos sur plusieurs comptes YouTube.
- Interface graphique simple pour choisir :
  - Le dossier contenant les vidéos.
  - Le fichier des comptes (`accounts.txt`).
  - Le fichier des titres (`titles.txt`).
  - Le fichier des descriptions (`descriptions.txt`).
  - Le fichier des proxys (`proxies.txt`).
- Gestion de plusieurs comptes avec création automatique de **credentials JSON**.
- Vérification de la durée des vidéos (max 25 secondes).
- Choix du nombre de vidéos à uploader par compte.
- Ajout d’un temps d’attente entre chaque upload.
- Système de rotation de proxys.
- Génération de logs (`output.log`) pour suivre l’état de chaque upload.

## 🛠️ Technologies utilisées
- **Python 3**
- **Tkinter** (interface graphique)
- **Google API Client** (`google-auth-oauthlib`, `google-api-python-client`)
- **OpenCV** (pour vérifier la durée des vidéos)
- **YouTube Data API v3**

## 📂 Organisation des fichiers
- `accounts.txt` → Liste des comptes à utiliser.
- `titles.txt` → Liste des titres pour les vidéos.
- `descriptions.txt` → Liste des descriptions.
- `proxies.txt` → Liste des proxys (optionnel).
- `output.log` → Historique des uploads.
- `error_log.txt` → Journal des erreurs critiques.

## ⚠️ Remarque
- Ce projet est fourni **à but éducatif** uniquement.  
- L’utilisation abusive de l’API YouTube peut entraîner la **suspension** de vos comptes.  
- Assurez-vous d’avoir un fichier `client_secret.json` valide fourni par Google Developer Console.  

## ▶️ Utilisation
1. Lancer le script :
   ```bash
   python youtube_uploader.py
