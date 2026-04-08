# Use Apify's base Python image with Playwright
FROM apify/actor-python-playwright:3.11

# Use a stable workdir for predictable build/runtime paths
WORKDIR /usr/src/app

# Install project dependencies
# Install runtime deps explicitly so Actor SDK modules are always available
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . ./

# Chromium already installed in base image

# Set the entry point
CMD ["python", "-m", "src.main"]

