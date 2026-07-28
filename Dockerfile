# Step 1: Use an official Python base image
FROM python:3.11-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the dependencies file to the working directory
COPY requirements.txt .

# Step 4: Install the Python dependencies
RUN pip install -r requirements.txt

# Step 5: Copy the application script to the working directory
COPY app.py .

# Step 6: Inform Docker that the container listens on port 8000
EXPOSE 9000

# Step 7: Define the command to run the application
CMD ["python", "app.py"]
