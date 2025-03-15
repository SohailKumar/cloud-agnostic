# Use the official Python image as a base image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the local code into the container
COPY . /app

# Install the required dependencies
RUN pip install Flask

# Expose port 8080 for the application
EXPOSE 8080

# Set the entry point for the application
CMD ["python", "app.py"]