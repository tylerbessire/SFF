# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Install Chrome and ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install \
    && wget https://chromedriver.storage.googleapis.com/89.0.4389.23/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm google-chrome-stable_current_amd64.deb chromedriver_linux64.zip \
    && apt-get clean

# Expose port (optional, if your application uses any ports)
# EXPOSE 8080

# Command to run the main script
CMD ["python", "main.py"]
