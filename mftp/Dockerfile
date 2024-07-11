# Base image of python v3.11.9-slim
FROM python:3.11.9-slim

# Configure IST timezone
ENV TZ="Asia/Kolkata"

# Setup the working directory as /app
WORKDIR /app

# Get requirements file into container
COPY requirements.txt .

# Install the rquirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy codebase
COPY . .

# Set the entrypoint
ENTRYPOINT [ "python", "mftp.py" ]
