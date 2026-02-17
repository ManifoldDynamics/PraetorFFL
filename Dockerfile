# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (none really needed for minimal Flask, but good practice)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (we will use a separate list for docker to avoid GUI libs)
COPY requirements.txt .

# Install dependencies
# Note: We filter out pywebview here manually or create a separate file.
# For simplicity, we just install everything, pywebview might fail without GTK but we won't import it.
RUN pip install --no-cache-dir flask fpdf2 gunicorn

# Copy app source
COPY . .

# Set environment variable to tell app we are in Docker
ENV DOCKER_MODE=true
ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/app/data

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 5000

# Run gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main_web:app"]
