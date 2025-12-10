FROM python:3.10-slim

# System dependencies not needed for pure python implementation
RUN apt-get update && apt-get install -y \
    android-tools-adb \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 1666

# Command to run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "1666"]
