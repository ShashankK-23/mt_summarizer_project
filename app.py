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
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

translator = Translator()

# 🔹 Tell pytesseract exactly where the tesseract executable is.
#    Update this path if your tesseract.exe is in a different folder.
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Home page
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

# OCR endpoint
@app.route('/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        return redirect(url_for('index'))
    file = request.files['image']
    if file.filename == '':
        return redirect(url_for('index'))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Perform OCR and handle errors gracefully
    try:
        text = pytesseract.image_to_string(Image.open(filepath))
    except Exception as e:
        # Return to index with a friendly error message (template may display it if you handle 'error')
        error_msg = f"Error running Tesseract: {e}"
        return render_template('index.html', ocr_text='', error=error_msg)

    return render_template('index.html', ocr_text=text)

# Translation endpoint
@app.route('/translate', methods=['POST'])
def translate():
    text = request.form.get('text')
    dest_lang = request.form.get('dest_lang')
    if not text or not dest_lang:
        return redirect(url_for('index'))
    translated = translator.translate(text, dest=dest_lang)
    return render_template('index.html', translated_text=translated.text)

# Summarization endpoint
@app.route('/summarize', methods=['POST'])
def summarize():
    text = request.form.get('text')
    if not text:
        return redirect(url_for('index'))
    parser = PlaintextParser.from_string(text, Tokenizer('english'))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 3)
    summary_text = ' '.join(str(sentence) for sentence in summary)
    return render_template('index.html', summary_text=summary_text)

if __name__ == '__main__':
    app.run(debug=True)
