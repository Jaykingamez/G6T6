# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt if you have one (optional)
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5210

# Command to run amqp_setup.py first to create queues, then start notification.py
CMD ["sh", "-c", "python amqp_setup.py && python notification.py"]
