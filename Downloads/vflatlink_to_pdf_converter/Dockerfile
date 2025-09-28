# Use official Python base image
FROM python:3.11-slim

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget unzip xvfb libnss3 libgconf-2-4 libxi6 libxcursor1 libxss1 libxcomposite1 libasound2 libatk1.0-0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y /tmp/chrome.deb \
    && rm /tmp/chrome.deb

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') \
    && wget -q -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip

# Set environment variables for headless Chrome
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_DRIVER=/usr/local/bin/chromedriver

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
