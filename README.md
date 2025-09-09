# PDF to Image Service 🚀

A high-performance, lightweight microservice for converting PDF documents to various image formats (JPEG, PNG, WEBP). Built with Flask and the blazing-fast libvips image processing library.

This project is designed for easy deployment in a Docker container.

[![Docker Ready](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/r/niklasbem/pdf2img/tags)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![libvips](https://img.shields.io/badge/powered%20by-libvips-green.svg)](https://libvips.github.io/libvips/)

## ✨ Key Features

- **🚀 Lightning Fast**: Leverages libvips for one of the fastest PDF-to-image conversions available
- **💾 Memory Efficient**: All processing happens in-memory with zero temporary files written to disk
- **🎛️ Flexible API**: Complete control over resolution (DPI), image size, output format, quality, and basic image filters
- **🐳 Docker Ready**: Optimized multi-stage Dockerfile for fast builds and minimal image sizes
- **🏭 Production Ready**: Runs with Gunicorn WSGI server, ready for deployment behind a reverse proxy
- **📊 Multi-page Support**: Convert single pages or entire documents efficiently
- **⚡ Batch Processing**: New batch endpoint for optimal multi-page conversion performance

## 🏁 Quick Start

The recommended way to run this service is using Docker.

### 1. Build Docker Image

Clone this repository and build the Docker image from the project root:

```bash
docker build -t pdf-image-service .
```

### 2. Run Container

Start a container from the built image. The service runs on port 5000 inside the container:

```bash
docker run -d -p 5000:5000 --name pdf-converter pdf-image-service
```

**Flag explanations:**

- `-d`: Run container in detached mode (background)
- `-p 5000:5000`: Map host port 5000 to container port 5000
- `--name pdf-converter`: Assign a memorable name to the container

The service is now available at `http://localhost:5000`.

## ⚙️ API Usage & Examples

The service provides two main endpoints:

- **`/image`** - Convert single pages or all pages (returns image file)
- **`/batch-images`** - Convert all pages efficiently (returns JSON with Base64 images) ⚡ **NEW**

Send POST requests with `multipart/form-data` to either endpoint.

### Example 1: Basic Conversion (PDF to JPEG)

Convert the first page of a PDF to JPEG with 150 DPI and 85% quality:

```bash
curl -X POST \
  -F "image=@document.pdf" \
  http://localhost:5000/image > output.jpeg
```

### Example 2: High-Resolution PNG Conversion

Convert PDF to PNG with 300 DPI:

```bash
curl -X POST \
  -F "image=@document.pdf" \
  -F "dpi=300" \
  -F "format=png" \
  http://localhost:5000/image > output.png
```

### Example 3: Create Thumbnail with Quality Control

Generate a thumbnail with maximum width of 800 pixels and 60% JPEG quality:

```bash
curl -X POST \
  -F "image=@document.pdf" \
  -F "width=800" \
  -F "quality=60" \
  http://localhost:5000/image > thumbnail.jpeg
```

### Example 4: Grayscale with Threshold

Convert the third page (page=2) to pure black and white. Grayscale values above 190 become white, below become black:

```bash
curl -X POST \
  -F "image=@document.pdf" \
  -F "page=2" \
  -F "grayscale=true" \
  -F "thresh=190" \
  http://localhost:5000/image > black-white.jpeg
```

### Example 5: Convert All Pages (Traditional Method)

Convert all pages of a PDF (use with caution for large documents):

```bash
curl -X POST \
  -F "image=@document.pdf" \
  -F "n=-1" \
  http://localhost:5000/image > all-pages.jpeg
```

### Example 6: Batch Convert All Pages ⚡ **NEW & RECOMMENDED**

Efficiently convert all pages to separate images using the new batch endpoint:

```bash
curl -X POST \
  -F "image=@document.pdf" \
  -F "dpi=150" \
  -F "format=jpeg" \
  http://localhost:5000/batch-images
```

**Response Example:**

```json
{
  "success": true,
  "total_pages": 3,
  "format": "jpeg",
  "dpi": 150,
  "images": [
    {
      "page": 1,
      "data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
    },
    {
      "page": 2,
      "data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
    },
    {
      "page": 3,
      "data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
    }
  ]
}
```

### Example 7: Batch Convert with Processing Options

Convert all pages with grayscale and custom quality:

```bash
curl -X POST \
  -F "image=@document.pdf" \
  -F "dpi=200" \
  -F "format=png" \
  -F "grayscale=true" \
  -F "width=1200" \
  http://localhost:5000/batch-images
```

## 📋 API Parameters

All parameters are sent as form fields (`-F` in cURL).

### `/image` Endpoint Parameters

| Parameter   | Description                                                                                                | Type    | Default    |
| ----------- | ---------------------------------------------------------------------------------------------------------- | ------- | ---------- |
| `image`     | **(Required)** The PDF file to upload                                                                      | File    | -          |
| `page`      | Page number to convert (0-indexed, so 0 is the first page)                                                 | Integer | 0          |
| `dpi`       | Resolution in dots per inch for rendering. Higher values = larger pixel dimensions                         | Integer | 150        |
| `width`     | Scale output image to fixed width in pixels. Aspect ratio is preserved                                     | Integer | (disabled) |
| `format`    | Output image format. Supported values: `jpeg`, `png`, `webp`                                               | String  | `jpeg`     |
| `quality`   | Output image quality. For jpeg/webp: 1-100. For png: compression level 0-9                                 | Integer | 85 (JPEG)  |
| `grayscale` | Convert image to grayscale. Set any value (e.g., `true` or `1`) to enable                                  | String  | (disabled) |
| `thresh`    | Apply threshold filter (ideal after grayscale). Values above threshold become white, below become black    | Integer | 128        |
| `n`         | Number of pages to process. `-1` means "all pages" ⚠️ **Warning**: Resource-intensive for large documents! | Integer | 1          |

### `/batch-images` Endpoint Parameters ⚡ **NEW**

| Parameter   | Description                                                                                             | Type    | Default    |
| ----------- | ------------------------------------------------------------------------------------------------------- | ------- | ---------- |
| `image`     | **(Required)** The PDF file to upload                                                                   | File    | -          |
| `dpi`       | Resolution in dots per inch for rendering. Higher values = larger pixel dimensions                      | Integer | 150        |
| `width`     | Scale output image to fixed width in pixels. Aspect ratio is preserved                                  | Integer | (disabled) |
| `format`    | Output image format. Supported values: `jpeg`, `png`, `webp`                                            | String  | `jpeg`     |
| `quality`   | Output image quality. For jpeg/webp: 1-100. For png: compression level 0-9                              | Integer | 85 (JPEG)  |
| `grayscale` | Convert image to grayscale. Set any value (e.g., `true` or `1`) to enable                               | String  | (disabled) |
| `thresh`    | Apply threshold filter (ideal after grayscale). Values above threshold become white, below become black | Integer | 128        |

**Key Differences:**

- `/batch-images` automatically processes **all pages** (no `page` or `n` parameter needed)
- Returns **JSON with Base64-encoded images** instead of a single image file
- **Much more efficient** for multi-page documents (single request vs. multiple requests)

## 🛠️ Local Development (without Docker)

If you want to run and modify the code directly:

### Install libvips

Ensure the libvips library and development headers are installed on your system:

- **macOS (Homebrew)**: `brew install vips`
- **Debian/Ubuntu**: `sudo apt-get update && sudo apt-get install libvips-dev`
- **CentOS/RHEL**: `sudo yum install vips-devel`
- **Windows**: Download from [libvips releases](https://github.com/libvips/libvips/releases)

### Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Start Flask Development Server

```bash
# Start development server
flask run

# Or with debug mode
flask --debug run
```

The service is now available at `http://127.0.0.1:5000`.

## 🔧 Configuration

### Environment Variables

| Variable    | Description                | Default      |
| ----------- | -------------------------- | ------------ |
| `FLASK_ENV` | Flask environment          | `production` |
| `PORT`      | Server port                | `5000`       |
| `WORKERS`   | Number of Gunicorn workers | `4`          |

### Production Deployment

For production use, consider:

1. **Reverse Proxy**: Use nginx or similar in front of the service
2. **Resource Limits**: Set appropriate memory/CPU limits in Docker
3. **Monitoring**: Add health checks and logging
4. **Security**: Implement rate limiting and file size restrictions

## 📊 Performance Notes

- **Memory Usage**: Roughly 50-100MB per concurrent conversion
- **Speed**: Typical conversion time is 100-500ms per page
- **Scaling**: Stateless design allows horizontal scaling
- **File Size Limits**: Default Flask limit is 16MB per request

### Performance Comparison: `/image` vs `/batch-images`

| Metric                     | `/image` (per page)    | `/batch-images` (all pages) |
| -------------------------- | ---------------------- | --------------------------- |
| **Network Requests**       | N requests for N pages | 1 request for N pages       |
| **HTTP Overhead**          | High (N × connection)  | Low (1 × connection)        |
| **Server Processing**      | N × PDF parsing        | 1 × PDF parsing             |
| **Recommended Use Case**   | Single pages, previews | Multi-page documents        |
| **Large PDFs (50+ pages)** | ❌ Inefficient         | ✅ **Highly Recommended**   |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [libvips](https://libvips.github.io/libvips/) - Fast image processing library
- [Flask](https://flask.palletsprojects.com/) - Lightweight web framework
- [Gunicorn](https://gunicorn.org/) - Python WSGI HTTP Server
