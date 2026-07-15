FROM python:3.11

# Install LibreOffice for Word→PDF conversion
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice \
        libreoffice-writer && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Verify LibreOffice is accessible
RUN soffice --version

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads

ENV PYTHONUNBUFFERED=1
ENV HOME=/root

EXPOSE 10000

CMD ["gunicorn", "--workers", "2", "--timeout", "120", "-b", "0.0.0.0:10000", "app:app"]
