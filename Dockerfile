# ---------- Base image ----------
FROM python:3.11-slim

# ---------- Dependencies ----------
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- App code ----------
COPY . .

# ---------- Runtime config ----------
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# ---------- Run ----------
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
    