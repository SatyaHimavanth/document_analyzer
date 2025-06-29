# Use a minimal Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy project files into the container
COPY . .

# Disable virtualenv creation and install dependencies globally
RUN poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction --no-ansi

# Expose FastAPI port
EXPOSE 8010

# Run your app
CMD ["python3", "main.py"]
