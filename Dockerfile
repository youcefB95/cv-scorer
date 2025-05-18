# ✅ Image de base légère avec Python
FROM python:3.10-slim

# ✅ Installer poppler-utils pour pdf2image
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# ✅ Définir le dossier de travail
WORKDIR /app

# ✅ Copier les fichiers nécessaires dans l'image
COPY . .

# ✅ Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# ✅ S'assurer que la police Unicode est bien incluse (facultatif)
RUN mkdir -p /usr/share/fonts/dejavu && cp fonts/DejaVuSans.ttf /usr/share/fonts/dejavu/

# ✅ Exposer le port pour Streamlit
EXPOSE 8501

# ✅ Commande pour démarrer l'application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
