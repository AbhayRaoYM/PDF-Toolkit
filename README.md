# PDF Toolkit

A Flask-based web application for common PDF and document operations, running entirely in your browser with no third-party cloud services.

🌐 **Live at: [https://pdf-toolkit-ksux.onrender.com](https://pdf-toolkit-nxi8.onrender.com)**

---

## Modules

| Module | Route | Description |
|--------|-------|-------------|
| Word → PDF | `/word-to-pdf` | Convert a `.docx` file to PDF |
| Merge PDFs | `/merge-pdf` | Combine multiple PDFs in drag-to-set order |
| Split PDF | `/split-pdf` | Split by page ranges or every page individually |
| PDF → Word | `/pdf-to-word` | Convert a PDF back to an editable `.docx` |

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

## To keep different versions
````
  git log --oneline
  git checkout -b old-ui <commit-id-before-redesign>
  git push origin old-ui
````

To switch Render to the old UI, go to Render dashboard → Settings → Branch → change from main to old-ui.

---

## Future Modules (Planned)

- Compress PDF
- Add watermark to PDF
- Extract images / PDF to PNG per page
- Rotate / reorder pages
- Password protect / unlock PDF
