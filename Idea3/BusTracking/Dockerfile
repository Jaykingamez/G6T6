# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY bus_tracking.py .

# Expose the port the app runs on
EXPOSE 5399

# Command to run the application
CMD ["python", "bus_tracking.py"]
