# Use a lightweight Python image as base
FROM python:3.10-slim


# Set working directory
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install dependencies (make sure requirements.txt is prepared)
RUN pip install --no-cache-dir -r requirements.txt

# Set the default command (can be overridden by docker-compose)
CMD ["python", "main.py", "--help"]
