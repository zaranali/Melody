# Builder stage
FROM python:3.13-slim as builder

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    git && \
    rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Final runtime stage
FROM python:3.13-slim

WORKDIR /app

# Non-root user for security
RUN groupadd -r botgroup && useradd -r -g botgroup botuser && \
    chown -R botuser:botgroup /app

# Runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Install only runtime dependencies
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy the rest of the application
COPY --chown=botuser:botgroup . .

# Pre-create downloads directory and ensure permissions
RUN mkdir -p downloads cache && \
    chown botuser:botgroup downloads cache

# Switch to non-root user
USER botuser

# Healthcheck to verify the bot's web service is alive
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

CMD ["bash", "start"]
