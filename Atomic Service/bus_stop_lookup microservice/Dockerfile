# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /usr/src/app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose Flask port
EXPOSE 5002

# Start the Flask app with data loading
CMD ["sh", "-c", "python load_bus_stops.py && python bus_stop_lookup.py"]