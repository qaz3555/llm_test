FROM python:3.10-slim

RUN pip install --no-cache-dir fastapi uvicorn httpx \
 && pip install huggingface_hub

WORKDIR /app
COPY app /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]