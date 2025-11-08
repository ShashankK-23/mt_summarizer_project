from flask import Flask, render_template, request, redirect, url_for
import pytesseract
from PIL import Image
from googletrans import Translator
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import pytesseract
from PIL import Image
from googletrans import Translator
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import os
from werkzeug.utils import secure_filename
import io
import tempfile
import secrets

try:
    import PyPDF2
except Exception:
    PyPDF2 = None

try:
    from pdfminer.high_level import extract_text as pdfminer_extract_text
except Exception:
    pdfminer_extract_text = None

try:
    from pdf2image import convert_from_path, convert_from_bytes
except Exception:
    convert_from_path = None
    convert_from_bytes = None

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Ensure Flask has a SECRET_KEY for session/flash. In production set the SECRET_KEY env var.
# Fallback: generate a random key for development (note: this will change on each restart).
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Optional: let user set TESSERACT_CMD and POPPLER_PATH via environment variables
if os.environ.get('TESSERACT_CMD'):
    pytesseract.pytesseract.tesseract_cmd = os.environ.get('TESSERACT_CMD')

POPPLER_PATH = os.environ.get('POPPLER_PATH')  # optional

translator = Translator()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Home page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/download_text', methods=['POST'])
def download_text():
    text = request.form.get('text') or ''
    filename = request.form.get('filename') or 'output.txt'
    b = text.encode('utf-8')
    return send_file(io.BytesIO(b), as_attachment=True, download_name=filename, mimetype='text/plain')


@app.route('/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        flash('No image file part')
        return redirect(url_for('index'))
    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        flash('No selected file or invalid file type')
        return redirect(url_for('index'))
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    # basic preprocessing could be added here
    try:
        text = pytesseract.image_to_string(Image.open(filepath))
    except Exception as e:
        text = ''
        flash('OCR error: %s' % str(e))
    return render_template('index.html', ocr_text=text, source_preview=filename)


@app.route('/pdf', methods=['POST'])
def pdf():
    if 'pdf' not in request.files:
        flash('No PDF file part')
        return redirect(url_for('index'))
    file = request.files['pdf']
    if file.filename == '' or not allowed_file(file.filename):
        flash('No selected file or invalid file type')
        return redirect(url_for('index'))
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    extracted_text = []

    # First try to extract text from the PDF (text-based PDFs)
    # 1) PyPDF2
    if PyPDF2 is not None:
        try:
            with open(filepath, 'rb') as fh:
                reader = PyPDF2.PdfReader(fh)
                for page in reader.pages:
                    try:
                        ptext = page.extract_text() or ''
                    except Exception:
                        ptext = ''
                    if ptext:
                        extracted_text.append(ptext)
        except Exception:
            # fall through to next extractor
            extracted_text = []

    # 2) pdfminer as a fallback (often better for certain PDFs)
    if not any(extracted_text) and pdfminer_extract_text is not None:
        try:
            # pdfminer returns a string for all pages
            pminer_text = pdfminer_extract_text(filepath)
            if pminer_text:
                # split into page-like blocks by double newlines to keep behavior
                extracted_text.extend([p for p in pminer_text.split('\n\n') if p.strip()])
        except Exception:
            pass

    # If no text obtained, try image-based OCR via pdf2image
    if not any(extracted_text):
        if convert_from_bytes is None:
            flash('pdf2image or poppler not available; cannot OCR scanned PDF. See README for setup.')
        else:
            try:
                with open(filepath, 'rb') as fh:
                    pdf_bytes = fh.read()
                images = convert_from_bytes(pdf_bytes, dpi=200, poppler_path=POPPLER_PATH) if POPPLER_PATH else convert_from_bytes(pdf_bytes, dpi=200)
                for img in images:
                    try:
                        ptext = pytesseract.image_to_string(img)
                    except Exception:
                        ptext = ''
                    extracted_text.append(ptext)
            except Exception as e:
                flash('Error converting PDF to images: %s' % str(e))

    full_text = '\n\n'.join([t for t in extracted_text if t])
    if not full_text:
        # Provide a clearer, actionable message for the user about why extraction failed
        parts = []
        parts.append('No text could be extracted from the provided PDF.')
        # Indicate which extractors were available
        parts.append(f"PyPDF2 available: {'yes' if PyPDF2 is not None else 'no'}")
        parts.append(f"pdfminer available: {'yes' if pdfminer_extract_text is not None else 'no'}")
        parts.append(f"pdf2image available: {'yes' if convert_from_bytes is not None else 'no'}")
        if convert_from_bytes is None:
            parts.append('pdf2image/poppler is not available on this server; scanned PDFs require Poppler. See README for setup instructions.')
        else:
            # pdf2image is available but conversion may have failed earlier
            parts.append('pdf2image is available — scanned PDF OCR would have been attempted, but produced no text (check image quality).')
        # Show environment hints (don't expose secrets)
        parts.append(f"Detected POPPLER_PATH: {POPPLER_PATH or 'not set'}")
        msg = ' '.join(parts)
        flash(msg)
    return render_template('index.html', pdf_text=full_text, source_preview=filename)


@app.route('/translate', methods=['POST'])
def translate():
    text = request.form.get('text')
    dest_lang = request.form.get('dest_lang')
    if not text or not dest_lang:
        flash('Missing text or target language')
        return redirect(url_for('index'))
    try:
        translated = translator.translate(text, dest=dest_lang)
        translated_text = translated.text
    except Exception as e:
        translated_text = ''
        flash('Translation error: %s' % str(e))
    return render_template('index.html', translated_text=translated_text)


@app.route('/summarize', methods=['POST'])
def summarize():
    text = request.form.get('text')
    sentences = request.form.get('sentences') or 3
    try:
        sentences = int(sentences)
    except Exception:
        sentences = 3
    if not text:
        flash('No text provided for summarization')
        return redirect(url_for('index'))
    parser = PlaintextParser.from_string(text, Tokenizer('english'))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences)
    summary_text = ' '.join(str(sentence) for sentence in summary)
    return render_template('index.html', summary_text=summary_text)


if __name__ == '__main__':
    app.run(debug=True)
