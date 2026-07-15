# PDF Toolkit

A Flask-based web application for common PDF and document operations, running entirely in your browser with no third-party cloud services.

🌐 **Live at: [https://pdf-toolkit-nxi8.onrender.com](https://pdf-toolkit-nxi8.onrender.com)**

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

### Integrations

| Feature | Route | Description |
|---------|-------|-------------|
| Send via Gmail | `/gmail/send` | Email any processed file directly via Gmail OAuth 2.0 |

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

## Gmail Integration Setup

The **Send via Gmail** feature uses Google OAuth 2.0 and the Gmail API to send processed files directly from the app.

### One-time Setup (Google Cloud Console)

1. Go to [console.cloud.google.com](https://console.cloud.google.com) → create a project
2. **APIs & Services → Library** → search `Gmail API` → **Enable**
3. **APIs & Services → Credentials** → **Create Credentials → OAuth client ID**
   - Application type: **Web application**
   - Authorised redirect URIs:
     ```
     http://localhost:5000/gmail/callback
     https://pdf-toolkit-ksux.onrender.com/gmail/callback
     ```
4. Download the JSON file and rename it `client_secret.json`
5. **APIs & Services → OAuth consent screen**
   - Add scope: `https://www.googleapis.com/auth/gmail.send`
   - Add your email as a test user

### Local setup

Place `client_secret.json` inside the `pdf-toolkit/` folder. It is gitignored and will never be committed.

### Render (production) setup

Since `client_secret.json` is gitignored, upload it via Render's **Secret Files** feature:

1. Render dashboard → your service → **Environment** tab
2. Scroll to **Secret Files** → click **Add Secret File**
3. Filename: `/opt/render/project/src/client_secret.json`
4. Paste the full contents of your `client_secret.json`
5. Save and redeploy

### How it works

```
User finishes processing a file
        ↓
Click "Gmail" in the nav → /gmail/send
        ↓
First time: "Sign in with Google" → Google OAuth consent screen
        ↓
Redirected back → compose form pre-filled with filename
        ↓
Enter recipient, optional subject & message → Send
        ↓
File sent as attachment via Gmail API ✅
```

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
| `google-auth` | Google OAuth 2.0 token handling |
| `google-auth-oauthlib` | OAuth flow for Gmail API |
| `google-api-python-client` | Gmail API client |
| `gunicorn` | Production WSGI server |
| `libreoffice` *(system)* | Word → PDF on Linux (Docker) |

---

## Security Notes

- `client_secret.json` is gitignored — **never commit it to version control**
- Gmail credentials are stored only in the Flask server-side session — never in the browser or database
- The app only requests the `gmail.send` scope — it cannot read, delete, or access any emails

---
