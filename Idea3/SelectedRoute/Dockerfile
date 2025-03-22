# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file first (for better caching)
COPY requirements.txt .

# Install dependencies including MySQL client
RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev build-essential && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application files
COPY selected_route.py .

# Expose the port the app runs on
EXPOSE 5000

# Set environment variable for database connection
ENV dbURL="your_own_db_uri"

# Command to run the application
CMD ["python", "selected_route.py"]
