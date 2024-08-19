# Use the official Python image with Poetry pre-installed
FROM python:3.11-slim


# Set the working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry
# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --no-dev

# Copy the rest of the application code
COPY . .

# Expose the port the server runs on
EXPOSE 8080

# Command to run the application using Uvicorn
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
