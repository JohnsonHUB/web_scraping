# Use the official tiangolo/uvicorn-gunicorn-fastapi image as a base image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Copy the requirements.txt file
COPY ./requirements.txt /app/requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the FastAPI app to the container
COPY ./app /app

# Specify the default command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]