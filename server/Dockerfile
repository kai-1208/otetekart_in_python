FROM python:3.11-slim

WORKDIR /app

# Improve output buffering so logs show up immediately in Docker
ENV PYTHONUNBUFFERED=1



COPY server.py .

EXPOSE 5000

CMD ["python", "server.py"]
