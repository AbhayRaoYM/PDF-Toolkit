FROM python:3.11-slim

# Install LibreOffice for Word→PDF conversion
RUN apt-get update && \
    apt-get install -y --no-install-recommends libreoffice && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads

ENV PYTHONUNBUFFERED=1

EXPOSE 10000

CMD ["gunicorn", "--workers", "2", "--timeout", "120", "-b", "0.0.0.0:10000", "app:app"]
