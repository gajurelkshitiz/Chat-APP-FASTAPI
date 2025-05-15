FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .
COPY .env /app/.env

# ENV PORT=8000
# ENV LOG_LEVEL=info
# ENV DEV_MODE=production

# Expose the application port
# EXPOSE 8000

# Use array syntax for CMD to avoid shell parsing issues
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]