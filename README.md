# PDF Toolkit

A Flask-based web application for common PDF and document operations, running entirely in your browser with no third-party cloud services.

🌐 **Live at: [https://pdf-toolkit-ksux.onrender.com](https://pdf-toolkit-ksux.onrender.com)**

---

## Modules

### Conversion

| Module | Route | Description |
|--------|-------|-------------|
| Word → PDF | `/word-to-pdf` | Convert a `.docx` file to a PDF document |
| PDF → Word | `/pdf-to-word` | Convert a PDF back to an editable `.docx` file |
| PDF → Images | `/pdf-to-images` | Render each PDF page as PNG or JPG (downloaded as ZIP) |
| Images → PDF | `/images-to-pdf` | Combine multiple JPG/PNG images into a single PDF |

### Organise

| Module | Route | Description |
|--------|-------|-------------|
| Merge PDFs | `/merge-pdf` | Combine multiple PDFs in drag-to-set order |
| Split PDF | `/split-pdf` | Split by page ranges or extract every page individually |
| Extract Text | `/extract-text` | Pull all text from a PDF and download as `.txt` |
| Compress PDF | `/compress-pdf` | Reduce PDF file size with High / Balanced / Max presets |

### Security

| Module | Route | Description |
|--------|-------|-------------|
| Password Protect / Unlock | `/password-pdf` | Add or remove password protection on any PDF |

---

## Running Locally

### Requirements

- Python 3.11+
- **For Word → PDF conversion only:** Microsoft Word (Windows / macOS) **or** LibreOffice (Linux / macOS).

### Install & Run

```bash
cd pdf-toolkit
pip install -r requirements.txt
python app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

---

## File Handling

Uploaded files are stored in an `uploads/<session-id>/` folder scoped to your browser session. Files persist across operations so you can reuse them (e.g. upload a PDF once and both merge and split it). To clear your session files, send a `POST /clear-session` request or restart the server.

The `uploads/` directory is excluded from version control.

---

## Deployment

The app is deployed on [Render](https://render.com) using Docker (see [`Dockerfile`](Dockerfile)). LibreOffice is installed inside the container to support Word → PDF conversion on Linux.

Every push to the `main` branch on GitHub triggers an automatic redeploy:

```bash
git add .
git commit -m "your change"
git push
```

---

## Version Control

To keep different versions (e.g. preserve an older UI):

```bash
git log --oneline
git checkout -b old-ui <commit-id>
git push origin old-ui
```

To switch Render to a different branch: Render dashboard → Settings → Branch.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `flask` | Web framework |
| `pypdf` | PDF read / write / merge / split / password |
| `pdf2docx` | PDF → Word conversion |
| `docx2pdf` | Word → PDF (Windows/macOS via MS Word) |
| `python-docx` | `.docx` file handling |
| `pymupdf` | PDF → Images, Compress PDF |
| `Pillow` | Image processing for Images → PDF |
| `img2pdf` | Lossless image to PDF conversion |
| `gunicorn` | Production WSGI server |
| `libreoffice` *(system)* | Word → PDF on Linux (Docker) |

---

## Future Modules (Planned)

- Add watermark to PDF
- Rotate / reorder pages
- Unlock / remove PDF password (standalone)
