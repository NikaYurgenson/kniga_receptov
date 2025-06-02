FROM python:3.10-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
COPY setup.py .

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

# Second stage
FROM python:3.10-slim

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Create a non-root user to run the app
RUN groupadd -r botuser && useradd -r -g botuser botuser && \
    mkdir -p /home/botuser && \
    chown -R botuser:botuser /home/botuser && \
    chown -R botuser:botuser /app

# Switch to non-root user
USER botuser

# Create volume for environment variables
VOLUME ["/app/.env"]

# Run the application with the recipe-bot entry point
CMD ["recipe-bot"]
