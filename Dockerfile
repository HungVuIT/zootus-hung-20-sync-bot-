FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY kbsync ./kbsync
COPY prompts ./prompts
COPY main.py .

# Runs one full sync and exits 0 on success, 1 on failure.
# docker run --rm -e GEMINI_API_KEY=... <image>            -> full daily job
# docker run --rm -e GEMINI_API_KEY=... <image> --limit 40 -> smoke test
ENTRYPOINT ["python", "main.py"]
