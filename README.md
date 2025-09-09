# PDF to Image Service 🚀

Ein performanter und schlanker Microservice zur Konvertierung von PDF-Dokumenten in verschiedene Bildformate (JPEG, PNG, WEBP). Basiert auf Flask und der extrem schnellen Bildverarbeitungsbibliothek libvips.

Dieses Projekt ist für den einfachen Einsatz in einem Docker-Container konzipiert.

## ✨ Key Features

- **Extrem schnell**: Nutzt libvips für eine der schnellsten PDF-zu-Bild-Konvertierungen
- **Ressourcenschonend**: Die Verarbeitung findet vollständig im Arbeitsspeicher statt – es werden keine temporären Dateien auf der Festplatte angelegt
- **Flexibles API**: Volle Kontrolle über Auflösung (DPI), Bildgröße, Zielformat, Qualität und einfache Bildfilter
- **Docker-Ready**: Ein optimiertes, schlankes Multi-Stage-Dockerfile für schnelle Builds und kleine Image-Größen
- **Produktionstauglich**: Läuft mit einem Gunicorn WSGI-Server und ist für den Einsatz hinter einem Reverse-Proxy vorbereitet

## 🏁 Getting Started

Die empfohlene Methode zur Ausführung des Services ist die Verwendung von Docker.

### 1. Docker-Image bauen

Klonen Sie dieses Repository und bauen Sie das Docker-Image mit folgendem Befehl im Hauptverzeichnis des Projekts:

```bash
docker build -t pdf-image-service .
```

### 2. Docker-Container starten

Starten Sie einen Container aus dem eben erstellten Image. Der Service wird auf Port 5000 des Containers ausgeführt. Wir mappen ihn hier auf den Port 5000 des Host-Systems.

```bash
docker run -d -p 5000:5000 --name pdf-converter pdf-image-service
```

- `-d`: Führt den Container im Hintergrund aus (detached mode)
- `-p 5000:5000`: Mappt Port 5000 des Hosts auf Port 5000 des Containers
- `--name pdf-converter`: Gibt dem Container einen leicht zu merkenden Namen

Der Service ist jetzt unter `http://localhost:5000` erreichbar.

## ⚙️ API-Nutzung & Beispiele

Senden Sie eine POST-Anfrage mit `multipart/form-data` an den `/image`-Endpunkt.

### Beispiel 1: Standardkonvertierung (PDF zu JPEG)

Konvertiert die erste Seite der PDF-Datei in ein JPEG-Bild mit 150 DPI und 85% Qualität.

```bash
curl -X POST \
  -F "image=@dokument.pdf" \
  http://localhost:5000/image > ergebnis.jpeg
```

### Beispiel 2: In PNG konvertieren mit höherer Auflösung

Konvertiert die PDF in ein PNG-Bild mit 300 DPI.

```bash
curl -X POST \
  -F "image=@dokument.pdf" \
  -F "dpi=300" \
  -F "format=png" \
  http://localhost:5000/image > ergebnis.png
```

### Beispiel 3: Bild verkleinern (Thumbnail) und Qualität anpassen

Erstellt ein Vorschaubild mit einer maximalen Breite von 800 Pixeln und einer JPEG-Qualität von 60%.

```bash
curl -X POST \
  -F "image=@dokument.pdf" \
  -F "width=800" \
  -F "quality=60" \
  http://localhost:5000/image > thumbnail.jpeg
```

### Beispiel 4: Graustufenbild mit Schwellenwert (Threshold)

Konvertiert die dritte Seite (page=2) in ein reines Schwarz-Weiß-Bild. Alle Grauwerte über 190 werden weiß, alle darunter schwarz.

```bash
curl -X POST \
  -F "image=@dokument.pdf" \
  -F "page=2" \
  -F "grayscale=true" \
  -F "tresh=190" \
  http://localhost:5000/image > schwarz-weiss.jpeg
```

## 📋 API-Parameter

Alle Parameter werden als Formularfelder (`-F` in cURL) gesendet.

| Parameter   | Beschreibung                                                                                                       | Typ     | Standardwert  |
| ----------- | ------------------------------------------------------------------------------------------------------------------ | ------- | ------------- |
| `image`     | **(Erforderlich)** Die hochzuladende PDF-Datei                                                                     | File    | -             |
| `page`      | Die zu konvertierende Seitenzahl (0-basiert, d.h. 0 ist die erste Seite)                                           | Integer | 0             |
| `dpi`       | Die Auflösung in "dots per inch", mit der die Seite gerendert wird. Beeinflusst die Pixelgröße des Bildes          | Integer | 150           |
| `width`     | Skaliert das Ausgabebild auf eine feste Breite in Pixeln. Das Seitenverhältnis bleibt erhalten                     | Integer | (deaktiviert) |
| `format`    | Das gewünschte Ausgabeformat. Unterstützte Werte: `jpeg`, `png`, `webp`                                            | String  | `jpeg`        |
| `quality`   | Die Qualität des Ausgabebildes. Bei jpeg/webp: 1-100. Bei png: Kompressionslevel 0-9                               | Integer | 85 (für JPEG) |
| `grayscale` | Konvertiert das Bild in Graustufen. Setzen Sie einen beliebigen Wert (z.B. `true` oder `1`), um dies zu aktivieren | String  | (deaktiviert) |
| `tresh`     | Wendet einen Schwellenwert an (ideal nach Graustufen). Werte über dieser Schwelle werden weiß, der Rest schwarz    | Integer | 128           |
| `n`         | Die Anzahl der zu verarbeitenden Seiten. `-1` bedeutet "alle Seiten" ⚠️ **Achtung**: Dies ist ressourcenintensiv!  | Integer | 1             |

## 🛠️ Lokale Entwicklung (ohne Docker)

Wenn Sie den Code direkt ausführen und bearbeiten möchten:

### libvips installieren

Stellen Sie sicher, dass die libvips-Bibliothek und deren Entwicklungsdateien auf Ihrem System installiert sind:

- **macOS (Homebrew)**: `brew install vips`
- **Debian/Ubuntu**: `sudo apt-get update && sudo apt-get install libvips-dev`

### Python-Umgebung einrichten

```bash
# Virtuelle Umgebung erstellen
python3 -m venv venv

# Umgebung aktivieren
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

### Flask-App starten

```bash
# Startet den Entwicklungs-Server
flask run
```

Der Service ist nun unter `http://127.0.0.1:5000` verfügbar.
