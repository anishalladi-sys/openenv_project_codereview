# FROM python:3.11-slim

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    openai==1.3.0 \
    pydantic==2.0.0 \
    fastapi==0.104.0 \
    uvicorn==0.24.0

# Copy all project files
COPY environment.py .
COPY inference.py .
COPY openenv.yaml .
COPY README.md .

# Make inference.py executable
RUN chmod +x inference.py

# Default command
CMD ["python", "inference.py", "--task", "syntax_review", "--steps", "5"]
