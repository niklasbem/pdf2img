FROM debian:bullseye-slim

LABEL author="Niklas Ben el Mekki" description="PDF to Image converter service"

ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    # Gunicorn-Settings
    PORT=80 \
    THREADS=4 \
    WORKERS=1 \
    TIMEOUT=300

WORKDIR $APP_HOME



RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        # WICHTIG: Build-Tools hinzufügen
        build-essential \
        python3-dev \
        # Deine bisherigen Abhängigkeiten
        libvips42 \
        libpoppler-glib8 \
        pkg-config \
        libvips-dev \
        python3 \
        python3-pip \
        python3-venv \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --system --create-home appuser
USER appuser

EXPOSE $PORT

CMD gunicorn --bind 0.0.0.0:$PORT --threads $THREADS --workers $WORKERS --timeout $TIMEOUT app:app