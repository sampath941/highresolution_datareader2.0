# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the environment file if needed (optional)
COPY .env .env

# Expose the port Flask is running on
EXPOSE 5000

# Run the Flask application using run.py as the entry point
CMD ["python", "run.py"]