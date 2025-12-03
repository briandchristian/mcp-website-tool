# Use Apify's base Python image with Playwright
FROM apify/actor-python-playwright:3.11

# Copy project files
COPY . ./

# Install dependencies from pyproject.toml
RUN pip install --no-cache-dir -e .

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Set the entry point
CMD ["python", "-m", "src.main"]

