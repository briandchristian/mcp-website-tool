# Use Apify's base Python image with Playwright
FROM apify/actor-python-playwright:3.11

# Copy project files
COPY . ./

# Install project dependencies
# apify and playwright are already in base image - don't override them
RUN pip install --no-cache-dir structlog

# Chromium already installed in base image

# Set the entry point
CMD ["python", "-m", "src.main"]

