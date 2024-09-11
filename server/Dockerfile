# Use the official Python image with Poetry pre-installed
FROM python:3.11-slim


# Set the working directory
WORKDIR /app

# Copy requirements.txt to the container
COPY requirements.txt .

# Install app dependencies
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Copy the rest of the application code
COPY . .

# Expose the port the server runs on
EXPOSE 8080

# Command to run the application using Uvicorn
ENTRYPOINT ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
