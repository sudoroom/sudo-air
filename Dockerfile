FROM python:3.12-slim

WORKDIR /app

# Disable Python output buffering for real-time logs
ENV PYTHONUNBUFFERED=1
ENV UV_SYSTEM_PYTHON=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY pyproject.toml .
COPY main.py .
COPY .env .

# Install dependencies with uv
RUN uv pip install paho-mqtt influxdb-client python-dotenv loguru

# Run the subscriber directly with python
CMD ["python", "main.py"]
