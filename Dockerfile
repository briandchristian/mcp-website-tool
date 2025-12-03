# Use Apify's base Python image with Playwright
FROM apify/actor-python-playwright:3.11

# Copy project files
COPY . ./

# Install only additional dependencies
# apify and playwright are already in base image
RUN pip install --no-cache-dir \
    structlog>=23.0.0

# Chromium already installed in base image

# Set the entry point
CMD ["python", "-m", "src.main"]

