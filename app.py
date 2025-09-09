from flask import Flask, request, send_file
import pyvips
import io

app = Flask(__name__)

MAX_DPI = 300

@app.route("/")
def hello():
    return """
    <h1>PDF to Image Converter</h1>
    <h2>Endpoints:</h2>
    <h3>/image (POST) - Single page conversion</h3>
    <p>Parameters: page, dpi, grayscale, thresh, format (png/jpeg/webp), quality (1-100), width (in pixels)</p>
    <p>Returns: Single image file</p>
    
    <h3>/batch-images (POST) - All pages conversion</h3>
    <p>Parameters: dpi, grayscale, thresh, format (png/jpeg/webp), quality (1-100), width (in pixels)</p>
    <p>Returns: JSON with all pages as base64 encoded images</p>
    <p>Example response: {"success": true, "total_pages": 5, "images": [{"page": 1, "data": "data:image/jpeg;base64,..."}, ...]}</p>
    """

@app.route("/image", methods=['POST'])
def image():
    f = request.files.get('image')
    if not f:
        return "Please provide input pdf file", 400

    try:
        page = request.form.get('page', default=0, type=int)
        n = request.form.get('n', default=-1, type=int)
        dpi = request.form.get('dpi', default=150, type=int)
        
        # Sicherheitslimit für DPI
        dpi = min(dpi, MAX_DPI)

        # PDF aus dem Speicher lesen
        pdf_buffer = f.read()
        image = pyvips.Image.pdfload_buffer(pdf_buffer, page=page, n=n, dpi=dpi)

        # Bildverarbeitung
        if request.form.get('grayscale'):
            image = image.colourspace('b-w')
        if request.form.get('thresh'):
            thresh_value = request.form.get('thresh', default=128, type=int)
            image = image.relational_const('more', thresh_value)

        # Bildgröße anpassen (falls 'width' angegeben)
        width = request.form.get('width', type=int)
        if width and width > 0:
            image = image.thumbnail_image(width)

        # Ausgabeformat und Qualität
        output_format = request.form.get('format', default='jpeg').lower()
        
        # Schreiboptionen
        write_options = {}
        mimetype = f'image/{output_format}'

        if output_format == 'jpeg':
            quality = request.form.get('quality', default=85, type=int)
            write_options = {'Q': quality, 'strip': True} # 'strip' entfernt Metadaten (kleinere Datei)
        elif output_format == 'png':
            compression = request.form.get('quality', default=6, type=int) # 0-9
            write_options = {'compression': compression, 'strip': True}
        elif output_format == 'webp':
            quality = request.form.get('quality', default=80, type=int)
            write_options = {'Q': quality, 'strip': True}
        else:
            return "Unsupported format. Use 'jpeg', 'png' or 'webp'", 400

        # Ausgabe-Puffer
        image_buffer = image.write_to_buffer(f'.{output_format}', **write_options)

        return send_file(io.BytesIO(image_buffer), mimetype=mimetype)

    except pyvips.Error as e:
        app.logger.error(f"PyVips Error: {e}")
        return f"Error processing PDF: {e}", 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return "Something went wrong", 500

@app.route("/batch-images", methods=['POST'])
def batch_images():
    """
    Konvertiert alle Seiten eines PDFs in separate Bilder und gibt sie als JSON mit Base64-kodierten Bildern zurück.
    """
    import base64
    from flask import jsonify
    
    f = request.files.get('image')
    if not f:
        return jsonify({"error": "Please provide input pdf file"}), 400

    try:
        dpi = request.form.get('dpi', default=150, type=int)
        dpi = min(dpi, MAX_DPI)
        
        # Ausgabeformat und Qualität
        output_format = request.form.get('format', default='jpeg').lower()
        
        # Schreiboptionen
        write_options = {}
        if output_format == 'jpeg':
            quality = request.form.get('quality', default=85, type=int)
            write_options = {'Q': quality, 'strip': True}
        elif output_format == 'png':
            compression = request.form.get('quality', default=6, type=int)
            write_options = {'compression': compression, 'strip': True}
        elif output_format == 'webp':
            quality = request.form.get('quality', default=80, type=int)
            write_options = {'Q': quality, 'strip': True}
        else:
            return jsonify({"error": "Unsupported format. Use 'jpeg', 'png' or 'webp'"}), 400

        # PDF aus dem Speicher lesen
        pdf_buffer = f.read()
        
        # Erst ermitteln wir die Anzahl der Seiten
        try:
            # Lade nur die erste Seite um die PDF-Eigenschaften zu bekommen
            temp_image = pyvips.Image.pdfload_buffer(pdf_buffer, page=0, n=1, dpi=dpi)
            # PyVips kann die Seitenanzahl nicht direkt ermitteln, also versuchen wir es anders
        except:
            pass
        
        # Wir laden alle Seiten einzeln, bis wir einen Fehler bekommen
        images_data = []
        page = 0
        
        while True:
            try:
                # Lade eine einzelne Seite
                image = pyvips.Image.pdfload_buffer(pdf_buffer, page=page, n=1, dpi=dpi)
                
                # Bildverarbeitung
                if request.form.get('grayscale'):
                    image = image.colourspace('b-w')
                if request.form.get('thresh'):
                    thresh_value = request.form.get('thresh', default=128, type=int)
                    image = image.relational_const('more', thresh_value)

                # Bildgröße anpassen (falls 'width' angegeben)
                width = request.form.get('width', type=int)
                if width and width > 0:
                    image = image.thumbnail_image(width)

                # Bild in Buffer schreiben
                image_buffer = image.write_to_buffer(f'.{output_format}', **write_options)
                
                # Base64 kodieren
                base64_image = base64.b64encode(image_buffer).decode('utf-8')
                images_data.append({
                    'page': page + 1,
                    'data': f'data:image/{output_format};base64,{base64_image}'
                })
                
                page += 1
                
            except pyvips.Error as e:
                # Wenn wir keine weitere Seite laden können, sind wir fertig
                if "not enough pages" in str(e).lower() or "page" in str(e).lower():
                    break
                else:
                    # Echter Fehler
                    raise e
            except Exception as e:
                # Anderer Fehler beim Laden der Seite
                break
        
        if not images_data:
            return jsonify({"error": "No pages could be processed from the PDF"}), 500
            
        return jsonify({
            "success": True,
            "total_pages": len(images_data),
            "format": output_format,
            "dpi": dpi,
            "images": images_data
        })

    except pyvips.Error as e:
        app.logger.error(f"PyVips Error: {e}")
        return jsonify({"error": f"Error processing PDF: {e}"}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": "Something went wrong"}), 500