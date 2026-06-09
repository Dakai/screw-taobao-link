FROM python:3.12-slim-bookworm
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5001
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5001/')" || exit 1
CMD ["gunicorn", "--preload", "-w", "4", "--timeout", "30", "--max-requests", "10000", "--max-requests-jitter", "1000", "-b", "0.0.0.0:5001", "app:app"]
