# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask runs on (default: 5000)
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py"]
