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

## Folder Structure
- `app.py` - Main Flask application
- `templates/` - HTML templates
- `static/` - CSS and static files

---

**Developed for educational/demo purposes.**
