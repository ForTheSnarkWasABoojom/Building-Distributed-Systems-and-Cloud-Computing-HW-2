# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Expose the Flask port
EXPOSE 5000

# Command to run the app
CMD ["python", "app.py"]
