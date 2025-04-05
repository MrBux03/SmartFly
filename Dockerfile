# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Expose port 8000 for the application
EXPOSE 8000

# Run gunicorn
# Use 0.0.0.0 to be accessible from outside the container
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "airline_integration_service.wsgi:application"] 