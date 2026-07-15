# PDF Toolkit — Project Documentation

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Project Structure](#3-project-structure)
4. [Setup & Running Locally](#4-setup--running-locally)
5. [Modules](#5-modules)
   - [Word to PDF](#51-word-to-pdf)
   - [Merge PDFs](#52-merge-pdfs)
   - [Split PDF](#53-split-pdf)
   - [PDF to Word](#54-pdf-to-word)
6. [API Reference](#6-api-reference)
7. [Session & File Handling](#7-session--file-handling)
8. [Frontend](#8-frontend)
9. [Deployment (Render.com)](#9-deployment-rendercom)
10. [Dependencies](#10-dependencies)
11. [Known Limitations](#11-known-limitations)
12. [Future Modules](#12-future-modules)

---

## 1. Project Overview

**PDF Toolkit** is a browser-based document utility web application built with Python and Flask. It provides four document processing modules accessible through a clean, minimal web interface. Files are processed on the server and returned directly to the browser for download — no third-party cloud services are involved.

**Live URL:** https://pdf-toolkit-ksux.onrender.com

**Core modules:**

| Module | Description |
|--------|-------------|
| Word → PDF | Convert a `.docx` Word document to PDF |
| Merge PDFs | Combine multiple PDFs into one, in user-defined order |
| Split PDF | Split a PDF by page ranges or extract every page individually |
| PDF → Word | Convert a PDF back to an editable `.docx` document |

---

## 2. Architecture

```
Browser (HTML/CSS/JS)
        │
        │  HTTP (multipart upload / JSON)
        ▼
Flask Application (app.py)
        │
        ├── routes/word_to_pdf.py   ──▶  modules/word_to_pdf.py  ──▶  docx2pdf / LibreOffice
        ├── routes/merge_pdf.py     ──▶  modules/merge_pdf.py    ──▶  pypdf
        ├── routes/split_pdf.py     ──▶  modules/split_pdf.py    ──▶  pypdf
        └── routes/pdf_to_word.py   ──▶  modules/pdf_to_word.py  ──▶  pdf2docx
                │
                ▼
        uploads/<session_id>/       (server-side session folder)
```

**Request flow:**
1. User uploads a file via the browser
2. Flask route receives the file and saves it to the session folder
3. The corresponding module function processes the file
4. The output file is streamed back to the browser as a download
5. The input file remains in the session folder for reuse

---

## 3. Project Structure

```
pdf-toolkit/
├── app.py                        # Flask app entry point, session management, blueprint registration
├── requirements.txt              # Python package dependencies
├── Dockerfile                    # Docker image definition for deployment
├── Procfile                      # Gunicorn start command (fallback for Render)
├── render.yaml                   # Render.com deployment configuration
├── .python-version               # Pins Python version to 3.11
│
├── modules/                      # Pure business logic — no Flask dependencies
│   ├── __init__.py
│   ├── word_to_pdf.py            # .docx → PDF conversion
│   ├── merge_pdf.py              # PDF merge logic
│   ├── split_pdf.py              # PDF split logic (ranges + all pages)
│   └── pdf_to_word.py            # PDF → .docx conversion
│
├── routes/                       # Flask blueprints — HTTP layer only
│   ├── __init__.py
│   ├── word_to_pdf.py            # Routes: GET /word-to-pdf, POST /word-to-pdf/convert
│   ├── merge_pdf.py              # Routes: GET /merge-pdf, POST /merge-pdf/upload, POST /merge-pdf/merge
│   ├── split_pdf.py              # Routes: GET /split-pdf, POST /split-pdf/upload, POST /split-pdf/split
│   └── pdf_to_word.py            # Routes: GET /pdf-to-word, POST /pdf-to-word/convert
│
├── templates/                    # Jinja2 HTML templates
│   ├── base.html                 # Shared layout with navigation bar
│   ├── index.html                # Home page with module cards
│   ├── word_to_pdf.html
│   ├── merge_pdf.html
│   ├── split_pdf.html
│   └── pdf_to_word.html
│
├── static/
│   ├── css/
│   │   ├── style.css             # Global styles
│   │   └── sortable-list.css     # Styles for the drag-and-drop file list (Merge page)
│   └── js/
│       └── main.js               # Shared JS — active nav link highlighting
│
└── uploads/                      # Runtime-only, gitignored — session upload folders
    └── <session_id>/
        ├── uploaded_file.pdf
        └── split_output/
```

---

## 4. Setup & Running Locally

### Prerequisites

- Python 3.11+
- **Word → PDF only:** Microsoft Word (Windows/macOS) or LibreOffice (Linux/macOS)
  - Install LibreOffice on Ubuntu/Debian: `sudo apt install libreoffice`

### Installation

```bash
cd pdf-toolkit
pip install -r requirements.txt
```

### Running

```bash
python app.py
```

Open your browser at **http://localhost:5000**.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-secret-key-change-in-production` | Flask session signing key — **must be changed in production** |
| `PORT` | `5000` | Port the server listens on |

Set a custom secret key:
```bash
# Windows PowerShell
$env:SECRET_KEY = "your-random-secret-key"
python app.py
```

---

## 5. Modules

### 5.1 Word to PDF

**File:** [`modules/word_to_pdf.py`](modules/word_to_pdf.py)

Converts a `.docx` file to PDF. The conversion engine is chosen automatically based on the operating system:

| Platform | Engine |
|----------|--------|
| Windows | `docx2pdf` → delegates to Microsoft Word |
| macOS | `docx2pdf` → delegates to Microsoft Word |
| Linux | LibreOffice headless (`soffice --headless --convert-to pdf`) |

**Function:**

```python
convert(docx_path: str, output_dir: str) -> str
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `docx_path` | `str` | Absolute path to the input `.docx` file |
| `output_dir` | `str` | Directory where the output PDF will be written |
| **Returns** | `str` | Absolute path to the output PDF file |

**`_find_soffice()` helper:**
On Linux, this helper searches for the LibreOffice binary by trying `soffice`, then `libreoffice` via `shutil.which()`, then falls back to the known Debian path `/usr/lib/libreoffice/program/soffice`.

---

### 5.2 Merge PDFs

**File:** [`modules/merge_pdf.py`](modules/merge_pdf.py)

Merges a list of PDF files into a single PDF in the order provided.

**Function:**

```python
merge(pdf_paths: list, output_path: str) -> str
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `pdf_paths` | `list[str]` | Ordered list of absolute paths to input PDF files |
| `output_path` | `str` | Absolute path for the output merged PDF |
| **Returns** | `str` | The `output_path` on success |

Uses `pypdf.PdfWriter` — iterates each input file, appends all pages in order, then writes the combined PDF.

---

### 5.3 Split PDF

**File:** [`modules/split_pdf.py`](modules/split_pdf.py)

Provides three functions for splitting and inspecting PDFs.

#### `get_page_count`

```python
get_page_count(pdf_path: str) -> int
```

Returns the total number of pages in a PDF.

#### `parse_range_string`

```python
parse_range_string(range_str: str) -> list[tuple]
```

Parses a human-readable range string into a list of `(start, end)` tuples (1-indexed, inclusive).

| Input | Output |
|-------|--------|
| `"1-3, 5, 7-10"` | `[(1,3), (5,5), (7,10)]` |
| `"2"` | `[(2,2)]` |
| `"1-5"` | `[(1,5)]` |

#### `split_by_ranges`

```python
split_by_ranges(pdf_path: str, ranges: list, output_dir: str) -> list[str]
```

Splits a PDF by the given page ranges. Each range produces one output PDF file named `<base>_part<n>_p<start>-p<end>.pdf`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `pdf_path` | `str` | Path to the input PDF |
| `ranges` | `list[tuple]` | List of `(start, end)` tuples, 1-indexed inclusive |
| `output_dir` | `str` | Directory for output files |
| **Returns** | `list[str]` | List of output file paths |

#### `split_all_pages`

```python
split_all_pages(pdf_path: str, output_dir: str) -> list[str]
```

Extracts every page into its own PDF file named `<base>_page<n>.pdf`.

---

### 5.4 PDF to Word

**File:** [`modules/pdf_to_word.py`](modules/pdf_to_word.py)

Converts a PDF to an editable `.docx` Word document using the `pdf2docx` library.

**Function:**

```python
convert(pdf_path: str, output_dir: str) -> str
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `pdf_path` | `str` | Absolute path to the input PDF file |
| `output_dir` | `str` | Directory where the output `.docx` will be written |
| **Returns** | `str` | Absolute path to the output `.docx` file |

> **Note:** Conversion quality depends on PDF type. Text-based PDFs convert well. Scanned image PDFs (no embedded text) will produce a document with images only, not editable text.

---

## 6. API Reference

All endpoints return JSON error responses on failure:
```json
{ "error": "Description of what went wrong." }
```

---

### `GET /`
Home page. Returns the landing page with module cards.

---

### `GET /word-to-pdf`
Renders the Word → PDF module page.

### `POST /word-to-pdf/convert`
Converts an uploaded `.docx` file to PDF.

**Request:** `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | File | The `.docx` file to convert |

**Response:** PDF file download (`application/pdf`)

**Errors:**

| Status | Condition |
|--------|-----------|
| `400` | No file provided, or file is not `.docx` |
| `500` | Conversion failed (LibreOffice error, corrupt file, etc.) |

---

### `GET /merge-pdf`
Renders the Merge PDFs module page. Passes `existing_files` (list of PDF filenames already in the session folder) to the template.

### `POST /merge-pdf/upload`
Uploads one or more PDF files to the session folder.

**Request:** `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `files` | File(s) | One or more `.pdf` files |

**Response:** `application/json`
```json
{ "files": ["document1.pdf", "document2.pdf"] }
```

### `POST /merge-pdf/merge`
Merges the specified files in the given order.

**Request:** `application/json`
```json
{ "files": ["document1.pdf", "document2.pdf", "document3.pdf"] }
```

**Response:** PDF file download (`application/pdf`) named `merged_<timestamp>.pdf`

**Errors:**

| Status | Condition |
|--------|-----------|
| `400` | Fewer than 2 files provided, or a file is not found in the session |
| `500` | Merge failed |

---

### `GET /split-pdf`
Renders the Split PDF module page.

### `POST /split-pdf/upload`
Uploads a PDF and returns its page count.

**Request:** `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | File | The `.pdf` file to split |

**Response:** `application/json`
```json
{ "filename": "report.pdf", "page_count": 12 }
```

### `POST /split-pdf/split`
Splits the uploaded PDF and returns a ZIP of the output files.

**Request:** `application/json`
```json
{
  "filename": "report.pdf",
  "mode": "range",
  "ranges": "1-3, 5, 7-10"
}
```

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `filename` | string | — | Filename of the uploaded PDF in the session |
| `mode` | string | `"range"` or `"all"` | Split mode |
| `ranges` | string | e.g. `"1-3, 5"` | Required when `mode` is `"range"` |

**Response:** ZIP file download (`application/zip`) named `<filename>_split.zip`

**Errors:**

| Status | Condition |
|--------|-----------|
| `400` | File not found, no valid ranges, range out of bounds |
| `500` | Split failed |

---

### `GET /pdf-to-word`
Renders the PDF → Word module page.

### `POST /pdf-to-word/convert`
Converts an uploaded PDF to a `.docx` file.

**Request:** `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | File | The `.pdf` file to convert |

**Response:** `.docx` file download (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`)

**Errors:**

| Status | Condition |
|--------|-----------|
| `400` | No file provided, or file is not `.pdf` |
| `500` | Conversion failed |

---

### `POST /clear-session`
Deletes all files in the current session folder and clears the session cookie.

**Response:** `application/json`
```json
{ "status": "cleared" }
```

---

## 7. Session & File Handling

Each browser session is assigned a unique ID (UUID hex) stored in a Flask session cookie. All uploaded and generated files are stored under:

```
uploads/<session_id>/
```

This folder is created automatically on the first request and persists for the lifetime of the session. Files uploaded in one module are available to other modules without re-uploading (e.g. a PDF uploaded in Merge can be used in Split).

**Session folder cleanup:**
- Call `POST /clear-session` to delete all files and reset the session
- The `uploads/` directory is excluded from version control via `.gitignore`
- On the free Render tier, the filesystem is ephemeral — all uploads are lost on restart or redeploy

---

## 8. Frontend

The frontend uses plain HTML, CSS, and vanilla JavaScript — no build tools or JavaScript frameworks.

### Templates

All pages extend [`templates/base.html`](templates/base.html) which provides:
- A sticky top navigation bar with links to all four modules
- Active link highlighting (current page highlighted in nav)
- A `{% block content %}` for page-specific content
- A `{% block extra_scripts %}` for page-specific JavaScript

### JavaScript pattern

Each module page's JavaScript follows the same pattern:
1. Listen for file input change and drag-and-drop events
2. `fetch()` to upload the file to the server
3. Receive JSON response, update the UI
4. `fetch()` to trigger processing
5. Receive binary response (`blob()`), create an object URL, trigger browser download

### SortableJS (Merge page only)

The Merge PDF page loads [SortableJS](https://sortablejs.github.io/Sortable/) from CDN for the polished drag-and-drop file list:

```html
<script src="https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js"></script>
```

Each list item carries a `data-filename` attribute. When the user clicks **Merge & Download**, JavaScript reads the current DOM order of `data-filename` values and sends them as the ordered `files` array in the merge request.

---

## 9. Deployment (Render.com)

The app is deployed on [Render.com](https://render.com) using Docker.

### Dockerfile

Located at [`Dockerfile`](Dockerfile). Key steps:

1. Base image: `python:3.11` (full Debian — required for LibreOffice apt dependencies)
2. Installs `libreoffice` and `libreoffice-writer` via `apt-get`
3. Runs `soffice --version` to verify the install at build time — **build fails if LibreOffice is missing**
4. Installs Python packages from `requirements.txt`
5. Exposes port `10000` (Render's default Docker port)
6. Starts the app with `gunicorn` (2 workers, 120s timeout)

### render.yaml

```yaml
services:
  - type: web
    name: pdf-toolkit
    runtime: docker
    envVars:
      - key: SECRET_KEY
        generateValue: true
```

> **Important:** The `runtime: docker` in `render.yaml` only applies when creating a **new** service. If the service was originally created as a Python service, it must be deleted and recreated via the Render dashboard with Docker runtime selected.

### Redeploying

Every push to the `main` branch on GitHub triggers an automatic redeploy:

```bash
git add .
git commit -m "your change"
git push
```

### Build times

| Scenario | Approximate time |
|----------|-----------------|
| Code-only change (no Dockerfile change) | 1–2 minutes |
| Dockerfile changed (apt layer invalidated) | 6–8 minutes |

---

## 10. Dependencies

### Python packages (`requirements.txt`)

| Package | Version | Purpose |
|---------|---------|---------|
| `flask` | latest | Web framework |
| `flask-session` | latest | Server-side session support |
| `python-docx` | latest | Read/write `.docx` files |
| `docx2pdf` | latest | Word → PDF on Windows/macOS via MS Word |
| `pypdf` | latest | PDF reading, writing, merging, splitting |
| `pdf2docx` | latest | PDF → `.docx` conversion |
| `gunicorn` | latest | Production WSGI server |

### System packages (Docker / Linux only)

| Package | Purpose |
|---------|---------|
| `libreoffice` | Word → PDF conversion on Linux |
| `libreoffice-writer` | LibreOffice Writer component for `.docx` support |

---

## 11. Known Limitations

| Limitation | Detail |
|------------|--------|
| **Word → PDF on Linux requires LibreOffice** | The `docx2pdf` library only supports Windows and macOS. On Linux, LibreOffice headless is used instead. LibreOffice must be installed on the host or inside the Docker container. |
| **PDF → Word quality** | `pdf2docx` works best on text-based PDFs. Scanned PDFs (image-only) will not produce editable text. Complex layouts (tables, multi-column) may not convert perfectly. |
| **Ephemeral filesystem on Render free tier** | Uploaded files are stored on the server's local disk. On Render's free tier, the disk is wiped on every redeploy or restart. Files do not persist across server restarts. |
| **Free tier sleep** | Render's free tier puts the service to sleep after 15 minutes of inactivity. The first request after sleep takes ~30 seconds to wake up. |
| **No file size limits enforced** | There is currently no server-side file size cap. Very large files may cause timeouts (gunicorn timeout is set to 120 seconds). |
| **No authentication** | The app has no login system. The `/debug/soffice` route is publicly accessible and should be removed before production use. |

---

## 12. Future Modules

These modules are planned for future development:

| Module | Library | Description |
|--------|---------|-------------|
| Compress PDF | `pypdf` or Ghostscript | Reduce PDF file size by re-compressing images |
| Add Watermark | `pypdf` or `reportlab` | Stamp text or image watermark on every page |
| PDF to Images | `pymupdf` (fitz) | Render each PDF page as a PNG or JPG file |
| Rotate / Reorder Pages | `pypdf` | UI to rotate individual pages and drag to reorder before saving |
| Password Protect / Unlock | `pypdf` | Encrypt a PDF with a user password, or remove encryption |
