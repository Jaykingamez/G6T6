# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY enable_notification.py invokes.py amqp_lib.py ./

# Expose the port the app runs on
EXPOSE 5302

# Command to run the application
CMD ["python", "enable_notification.py"]
