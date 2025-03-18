# Use official Python image as a base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements.txt to the container
COPY requirements.txt ./

# Install Python dependencies from requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./emission.py .

# Run the Flask application
CMD [ "python", "./emission.py" ]
