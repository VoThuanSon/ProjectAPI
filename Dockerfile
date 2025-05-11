FROM python:3.10-slim

EXPOSE 8000

WORKDIR /app

# Copy requirements if available
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt || true

# Copy entire project
COPY . .

# Set default command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]