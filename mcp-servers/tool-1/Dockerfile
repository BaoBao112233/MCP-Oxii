FROM python:3.10-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml .
COPY main.py .

# Configure poetry to not use virtualenvs inside Docker
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root

# Expose the port
EXPOSE 9011

# Run the application
CMD ["python", "main.py"] 