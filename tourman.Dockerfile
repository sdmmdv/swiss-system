# docker/Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code
COPY src/ ./src
COPY db/ ./db
COPY tests/ ./tests

# Set PYTHONPATH for imports
ENV PYTHONPATH=/app/src

# Default command (can be overridden by docker-compose)
CMD ["./src/main.py --help"]
