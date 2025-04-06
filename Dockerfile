# Dockerfile

# 1. Use an official Python runtime as a parent image
# Using 3.12 based on your previous tracebacks, slim is smaller
FROM python:3.12-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1 # Prevents python from writing pyc files
ENV PYTHONUNBUFFERED 1 # Prevents python from buffering stdout/stderr

# 3. Set the working directory in the container
WORKDIR /app

# 4. Install dependencies
# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .
# Install pip dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the backend application code into the container
# This assumes your backend code is in a 'backend' subfolder
COPY ./backend /app/backend

# 6. Expose the port the app runs on
EXPOSE 8000

# 7. Define the command to run the application
# Use 0.0.0.0 to allow connections from outside the container
# Omit --reload for production images
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]