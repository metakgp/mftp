# Base image of python v3.11.8
FROM python:3.11.8

# Configure IST timezone
ENV TZ="Asia/Kolkata"

# Setup the working directory as /mftp-doctor
WORKDIR /mftp-doctor

# Get requirements file into container
COPY requirements.txt .

# Install the rquirements
RUN pip3 install -r requirements.txt

# Copy mftp-doctor.py script
COPY mftp-doctor.py .

# Set the entrypoint
ENTRYPOINT [ "python", "mftp-doctor.py" ]