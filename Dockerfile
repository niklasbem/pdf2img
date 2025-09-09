# Stage 1: Finale, schlanke Stage
# Wir verwenden bullseye, da es viel aktueller ist und die benötigten Pakete enthält.
FROM debian:bullseye-slim

# Metadaten
LABEL author="Your Name" description="PDF to Image converter service"

# Umgebungsvariablen für die Anwendung
ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    # Gunicorn-Settings
    PORT=5000 \
    THREADS=4 \
    WORKERS=1 \
    TIMEOUT=300

WORKDIR $APP_HOME

# 1. Systemabhängigkeiten installieren (nur Laufzeit!)
# - apt-get update, install und clean in einem RUN-Befehl, um Layer-Größe zu reduzieren
# - --no-install-recommends spart viel Platz
# - libvips-dev wird für die Installation von pyvips benötigt, kann aber später entfernt werden (siehe Multi-stage)
#   Für Einfachheit lassen wir es hier erstmal drin, für die ultra-optimierte Version siehe Version B.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        # Laufzeit-Abhängigkeiten für libvips und poppler
        libvips42 \
        libpoppler-glib8 \
        # Build-Abhängigkeit für pyvips (wird für pip install benötigt)
        pkg-config \
        libvips-dev \
        # Python
        python3 \
        python3-pip \
        python3-venv \
    # Aufräumen
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 2. Python Virtual Environment erstellen
RUN python3 -m venv /opt/venv
# Wichtig: venv zum PATH hinzufügen, damit wir nicht immer /opt/venv/bin/... schreiben müssen
ENV PATH="/opt/venv/bin:$PATH"

# 3. Python-Abhängigkeiten installieren (nutzt den Build-Cache)
# Erst requirements.txt kopieren und installieren. Wenn sich die Datei nicht ändert, wird dieser Layer wiederverwendet.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 4. Anwendungs-Code kopieren
COPY . .

# 5. Non-Root-User für die Ausführung erstellen und verwenden (Sicherheit!)
RUN useradd --system --create-home appuser
USER appuser

# Port freigeben
EXPOSE $PORT

# Anwendung starten
# CMD statt ENTRYPOINT ist oft flexibler
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--threads", "$THREADS", "--workers", "$WORKERS", "--timeout", "$TIMEOUT", "app:app"]