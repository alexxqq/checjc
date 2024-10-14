FROM python:3.9

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set environment variables
ENV FLASK_APP=app:app

# Command to run the application (no migrations here)
CMD ["flask", "run", "--host=0.0.0.0", "--port=6999"]
