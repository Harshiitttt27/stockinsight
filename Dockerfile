# Use official slim image
FROM python:3.11-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    nodejs \
    npm \
 && apt-get clean

# Install tailwind
RUN npm install -g tailwindcss

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy entire project
COPY . .

#  Add this line to ensure env vars are present
COPY .env .env

# Build Tailwind assets
RUN python manage.py tailwind install
RUN python manage.py tailwind build

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run Gunicorn server
CMD ["gunicorn", "stock_insight.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
