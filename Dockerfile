FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (this leverages uv's cache)
# We use --no-install-project to only install dependencies first
RUN uv sync --no-install-project --frozen

# Copy the rest of the application code
COPY . .

# Copy and ensure entrypoint is executable
COPY scripts/entrypoint.sh /app/scripts/entrypoint.sh
RUN chmod +x /app/scripts/entrypoint.sh

# Sync the project itself
RUN uv sync --frozen

# Expose the API port
EXPOSE 3009

# Run the entrypoint script
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
