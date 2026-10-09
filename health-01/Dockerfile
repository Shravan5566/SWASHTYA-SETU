FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (for building psycopg2 or crypto if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Set default environment variables
ENV PORT=5000 \
    FLASK_ENV=production \
    DEBUG=False \
    PYTHONUNBUFFERED=1

EXPOSE 5000

# Initialize and seed database if empty, then start server
CMD python seed.py && python run.py
