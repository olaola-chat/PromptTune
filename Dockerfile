# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies required for Poetry
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy poetry files
COPY pyproject.toml poetry.lock ./

COPY .env .

RUN poetry --version

# Configure Poetry to not create a virtual environment inside the container
RUN poetry config virtualenvs.create false

# Install dependencies (updated command)
RUN poetry install --no-interaction --no-ansi

# Copy the rest of the application code
COPY . .

# Create a non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 61188

# Command to run the application using Gunicorn with optimized worker configuration
CMD ["gunicorn", "--bind", "0.0.0.0:61188", "--timeout", "300", "--workers", "4", "--threads", "2", "app:app"]
