# Multilingual OCR, Translation & Summarization Web App

This is a Python Flask web application for multilingual OCR, translation, and summarization (text-to-text only) targeting Indian regional languages. No speech processing is included.

## Features
- **OCR**: Extract text from uploaded images (supports Indian languages)
- **Translation**: Translate text between Indian regional languages
- **Summarization**: Summarize long texts for quick understanding

## Tech Stack
- Python 3
- Flask
- pytesseract (OCR)
- googletrans (Translation)
- sumy (Summarization)
- HTML/CSS (Frontend)

## Setup Instructions

1. **Install Tesseract OCR**
   - Download and install from: https://github.com/tesseract-ocr/tesseract
   - Add Tesseract to your system PATH or specify its path in `app.py` if needed.

2. **Install Python dependencies**
   ```powershell
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the Flask app**
   ```powershell
   .venv\Scripts\activate
   python app.py
   ```
   The app will be available at http://127.0.0.1:5000/

## Usage
- Upload an image for OCR to extract text.
- Paste or type text for translation or summarization.
- Select the target language for translation.

## Notes
- For best OCR results, use clear images with printed text.
- Translation uses Google Translate API (free tier, may have limits).
- Summarization uses the LSA algorithm (English only by default).

### PDF / Poppler
- To OCR scanned PDFs the app uses pdf2image which requires Poppler. On Windows install Poppler and provide its bin path via the environment variable `POPPLER_PATH` or add it to your PATH.
- Poppler downloads: https://poppler.freedesktop.org/ or for Windows builds see https://github.com/oschwartz10612/poppler-windows

### Tesseract
- Install Tesseract OCR and either add it to your PATH or set the `TESSERACT_CMD` environment variable to the full path of `tesseract.exe`.

### Environment variables (optional)
- `TESSERACT_CMD`: full path to tesseract executable (e.g. `C:\Program Files\Tesseract-OCR\tesseract.exe`).
- `POPPLER_PATH`: path to poppler `bin` folder if not added to PATH.

## Docker + Hosting (recommended)

This project is easiest to deploy reliably using Docker because the container can include system packages (Tesseract, Poppler) that are required for OCR and PDF processing.

### Dockerfile
A `Dockerfile` is included in the repository. It installs Tesseract and Poppler utilities and runs the app with `gunicorn`.

### Build and run locally with Docker
1. Build the image (from repo root):

```powershell
docker build -t mt_summarizer:latest .
```

2. Run the container locally (forward port 5000):

```powershell
docker run --rm -p 5000:5000 mt_summarizer:latest
```

Open http://127.0.0.1:5000/ to verify.

If Tesseract or Poppler are not included in the image for any reason, you can pass explicit environment variables when running:

```powershell
docker run --rm -p 5000:5000 -e TESSERACT_CMD="C:\\Program Files\\Tesseract-OCR\\tesseract.exe" mt_summarizer:latest
```

### Deploy to Fly.io (free tier available)
Fly.io supports deploying Docker images and gives you a globally served app with automatic TLS. Quick steps:

1. Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
2. Login and create an app (from your repo folder):

```bash
fly auth login
fly launch
```

During `fly launch` choose a name, region, and it will detect the Dockerfile and create a `fly.toml` file. To deploy:

```bash
fly deploy
```

To provide any runtime environment variables (e.g., secrets or custom Tesseract/Poppler paths):

```bash
fly secrets set TESSERACT_CMD="/usr/bin/tesseract"
fly secrets set POPPLER_PATH="/usr/bin"
```

Fly will build your image and run it. Monitor logs with:

```bash
fly logs
```

### Deploy to Render (alternate)
Render also supports Docker and automatic deploys from GitHub. On Render:

1. Create a new Web Service and connect your GitHub repo.
2. Choose Docker as the environment (it will use your Dockerfile).
3. Set environment variables (TESSERACT_CMD / POPPLER_PATH) in the Render dashboard if needed.

### Notes on free tiers
- Free plans impose resource and uptime limits. For OCR and PDF processing, keep the uploads small and consider asynchronous/background processing for large files.
- The container will have ephemeral filesystem — uploads placed on disk are temporary; for persistent storage use S3, Backblaze or similar.

If you want, I can:
- Add a production-ready `fly.toml` template and a minimal GitHub Actions workflow that deploys on push to `main`.
- Add a simple health-check endpoint and small systemd/gunicorn tuning to improve startup and reliability.

### CI/CD: GitHub Actions (build image and optional Fly deploy)

There's a workflow included at `.github/workflows/ci-deploy.yml` that does two things on push to `main`:

- Builds a Docker image and pushes it to GitHub Container Registry (GHCR) as `ghcr.io/<your-username>/mt_summarizer:latest` and with the commit SHA tag.
- Optionally deploys that image to Fly.io if you add the following repository secrets:
   - `FLY_API_TOKEN` — your Fly API token (create via `fly auth token` or in the Fly dashboard)
   - `FLY_APP_NAME` — the Fly app name to deploy to (create the app via `fly launch` or the Fly dashboard)

To enable the automatic Fly deploy:

1. Create a Fly app (locally or in the Fly dashboard) and note its name.
2. Add `FLY_APP_NAME` and `FLY_API_TOKEN` to your GitHub repository secrets (Settings → Secrets → Actions).

When those secrets are present the workflow will authenticate to Fly and run `flyctl deploy --image <GHCR image> --app <FLY_APP_NAME>`.

If you prefer, I can also add an alternative workflow that deploys to Render or pushes images to Docker Hub instead.


## Folder Structure
- `app.py` - Main Flask application
- `templates/` - HTML templates
- `static/` - CSS and static files

---

**Developed for educational/demo purposes.**
