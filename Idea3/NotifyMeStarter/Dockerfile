# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY amqp_lib.py .
COPY notify_me_starter.py .

# Expose Port Number
EXPOSE 5302

# Set environment variables if needed
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python", "notify_me_starter.py"]
