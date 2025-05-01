FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for ffmpeg and weasyprint
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p ./uploads ./output

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
