# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt if you have one (optional)
# If you don't have a requirements.txt, you can install packages directly in the next step
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5205

# Command to run the application
CMD ["python", "check_balance.py"]