# Use Apify's base Python image with Playwright
FROM apify/actor-python-playwright:3.11

# Copy project files
COPY . ./

# Install compatible dependency versions
RUN pip install --no-cache-dir \
    apify==2.3.0 \
    playwright>=1.40.0 \
    pydantic==2.9.2 \
    structlog>=23.0.0

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Set the entry point
CMD ["python", "-m", "src.main"]

