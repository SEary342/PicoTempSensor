FROM python:3.14-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy the pico directory (for the shared_html import)
COPY pico/ ./pico/

# Copy the server application file
COPY app.py ./

# Install dependencies
RUN uv pip install --system flask gunicorn

EXPOSE 5000

# Set PYTHONPATH so 'import pico.shared_html' resolves correctly
ENV PYTHONPATH=/app

# Run gunicorn pointing to app.py in the current directory
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "app:app"]