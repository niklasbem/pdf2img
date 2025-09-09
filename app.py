from flask import Flask, request, send_file
import pyvips
import io

app = Flask(__name__)

MAX_DPI = 300

@app.route("/")
def hello():
    return "Use /image endpoint. Parameters: page, dpi, grayscale, thresh, format (png/jpeg/webp), quality (1-100), width (in pixels)"

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