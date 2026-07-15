# PDF Toolkit

A Flask-based web application for common PDF and document operations, running entirely in your browser with no third-party cloud services.

## Modules

| Module | Route | Description |
|--------|-------|-------------|
| Word → PDF | `/word-to-pdf` | Convert a `.docx` file to PDF |
| Merge PDFs | `/merge-pdf` | Combine multiple PDFs in drag-to-set order |
| Split PDF | `/split-pdf` | Split by page ranges or every page individually |
| PDF → Word | `/pdf-to-word` | Convert a PDF back to an editable `.docx` |

## Setup

### Requirements

- Python 3.9+
- **For Word → PDF conversion only:** Microsoft Word (Windows / macOS) **or** LibreOffice (Linux / macOS). The `docx2pdf` library delegates the actual conversion to one of these tools. Install LibreOffice on Linux with `sudo apt install libreoffice`.

### Install Python dependencies

```bash
cd pdf-toolkit
pip install -r requirements.txt
```

## Running the App

```bash
python app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

## File Handling

Uploaded files are stored in a `uploads/<session-id>/` folder scoped to your browser session. Files persist across operations so you can reuse them (e.g. upload a PDF once and both merge and split it). To clear your session files, send a `POST /clear-session` request or restart the server.

The `uploads/` directory is excluded from version control.

## Future Modules (Planned)

- Compress PDF
- Add watermark to PDF
- Extract images / PDF to PNG per page
- Rotate / reorder pages
- Password protect / unlock PDF
