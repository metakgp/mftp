# Multistage builds for reducing image size: https://mukul-mehta.in/til/reducing-container-size/

# Builder image for installing dependencies
FROM python:3.10-slim AS builder

# To allow pip to run as root
ENV PIP_ROOT_USER_ACTION=ignore

# Create a virtual environment for installing packages
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies in the builder image
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Image for the application
FROM python:3.10-slim

# Copy dependencies from the builder image
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source files
WORKDIR /app
COPY src/ .

# Run the app
CMD ["python", "main.py"]