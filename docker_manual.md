# Docker for Beginners: Hands-On Guide & Command Reference

This guide is a step-by-step teaching manual designed to introduce beginners to the core concepts of Docker using a simple **Python Flask To-Do application**.

---

## 📖 The Big Picture: What is Docker?
Think of a computer as a kitchen. Running apps directly on your computer is like cooking different recipes on the same counter at the same time—ingredients get mixed up, and dependencies clash.
*   **Docker Container**: A mini, self-contained kitchen with its own counter, utensils, and ingredients. Nothing leaks in or out.
*   **Docker Image**: A read-only blueprint or recipe book for setting up that mini-kitchen.

---

## Step 1: The Dockerfile (The Recipe)
A `Dockerfile` is a list of steps to build your image. Open the `Dockerfile` in the project. You will see these lines:

```dockerfile
# 1. Use an official Python base image
FROM python:3.11-slim

# 2. Set the folder inside the container where our code will live
WORKDIR /app

# 3. Copy only the list of dependencies first
COPY requirements.txt .

# 4. Install dependencies (Flask) inside the container
RUN pip install -r requirements.txt

# 5. Copy the actual app.py script into the container
COPY app.py .

# 6. Inform Docker that the app inside listens on port 8000
EXPOSE 8000

# 7. Start the application when the container turns on
CMD ["python", "app.py"]
```

### 💡 Teaching Point: The Build Cache
*   **How it works**: Docker builds the image layer-by-layer. If nothing changes in a step, Docker reuses a pre-saved "cache" of that layer.
*   **Why copy requirements.txt first?** Python packages take time to install. By copying `requirements.txt` and running `pip install` *before* copying `app.py`, Docker can cache the installed packages. When students edit `app.py`, Docker reuses the cached packages and builds the image in less than a second!

---

## Step 2: Build the Image
To build the image, run this command in your terminal:
```bash
docker build -t my-first-todo .
```
*   `-t my-first-todo`: Names (tags) our image `my-first-todo`.
*   `.`: Tells Docker to look for the `Dockerfile` in the current folder.

---

## Step 3: Run the Container (Ports & Running)
Now, turn the image recipe into a running container:
```bash
docker run -d -p 8080:8000 --name running-todo my-first-todo
```
*   `-d`: Runs the container in **detached mode** (in the background, freeing up the terminal).
*   `-p 8080:8000`: **Port publishing**. Connects port `8080` on your host computer to port `8000` inside the container.
*   `--name running-todo`: Gives a friendly name to the container.
*   `my-first-todo`: The image we want to run.

**Test it**: Open your browser and go to `http://localhost:8080`. Add a few tasks!

---

## Step 4: Container Ephemerality (The Data Problem)
Have students do this experiment to understand container disk behavior:
1. Add 2 tasks to your To-Do list on the webpage.
2. Stop and delete the container:
   ```bash
   docker rm -f running-todo
   ```
3. Run the container again:
   ```bash
   docker run -d -p 8080:8000 --name running-todo my-first-todo
   ```
4. Refresh `http://localhost:8080`. **The tasks are gone!**

**Why?** Containers are *ephemeral*. Files created inside a container (like `todos.json`) are deleted forever when the container is removed.

---

## Step 5: Persisting Data (Docker Volumes)
To save data permanently, we use **Volumes**. Think of a Volume as a USB flash drive managed by Docker that stays plugged in even if you replace the computer container.

Run the container with a volume:
```bash
docker run -d -p 8080:8000 \
  -v todo_data:/app/data \
  -e TODO_FILE=/app/data/todos.json \
  --name persistent-todo my-first-todo
```
*   `-v todo_data:/app/data`: Creates a volume named `todo_data` and mounts it to `/app/data` inside the container.
*   `-e TODO_FILE=/app/data/todos.json`: Tells our Python app to write the `todos.json` file inside that volume folder.

**Test persistence**: Add tasks, delete the container, run the command again, and verify the tasks are still there!

---

## Step 6: Sharing Files (Bind Mounts)
Volumes are managed by Docker. But what if you want to edit your code locally and see changes instantly without rebuilding the image? We use a **Bind Mount**.

```bash
docker run -it -p 8080:8000 \
  -v "$(pwd)":/app \
  --name dev-todo my-first-todo
```
*   `-v "$(pwd)":/app`: Links the current folder on your host computer (`$(pwd)`) to the `/app` folder inside the container.
*   Now, if you edit the HTML styling inside `app.py` on your computer, the container sees the file change immediately.

---

## Step 7: Docker Compose (The Easy Way)
Running long commands with multiple `-v`, `-p`, and `-e` flags is tedious. **Docker Compose** lets you define your container configuration in a single file: `docker-compose.yml`.

Run the entire application with one command:
```bash
docker compose up -d
```
*   This reads the `docker-compose.yml` file, builds the image, sets up the volume, sets the port mapping, and starts the container in the background.

To stop it and clean up:
```bash
docker compose down
```
*(Your data remains safe in the volume!)*

---

## Step 8: Pushing the Image to Docker Hub
To share your Docker image with others or deploy it to a server, you can push it to a Docker registry like **Docker Hub**. Follow these step-by-step instructions:

1. **Create a Docker Hub Account**: If you don't have one, sign up at [hub.docker.com](https://hub.docker.com/).
2. **Login to Docker Hub via Terminal**:
   ```bash
   docker login
   ```
   *You will be prompted to enter your Docker Hub username and password (or a Personal Access Token).*
3. **Tag your Image**: You must rename (tag) your image to include your Docker Hub username.
   ```bash
   docker tag my-first-todo <your_username>/my-first-todo:v1.0
   ```
   *(Replace `<your_username>` with your actual Docker Hub username).*
4. **Push the Image**: Upload your tagged image to Docker Hub.
   ```bash
   docker push <your_username>/my-first-todo:v1.0
   ```
5. **Verify**: Go to your Docker Hub account in the browser, and you will see your new repository and image!

---

## Step 9: Real-World Case Study: Building & Dockerizing a Machine Learning Application (`mlapp` / NeuralEdu Predictor)

In this real-world example, we build and containerize **NeuralEdu Predictor** (a Student Performance Predictor ML application) using Python, scikit-learn, Flask, Gunicorn, and Docker. The machine learning model predicts student final exam scores based on study habits, attendance, and demographics.

### 📁 Application File Structure

```text
mlapp/
├── data/                  # 📊 Data folder
│   └── dataset.csv        # Historical student dataset (1,000 records)
├── models/                # 🤖 Serialized ML models & pipelines
│   ├── linear_model.pkl   # Trained scikit-learn LinearRegression model
│   └── pipeline.joblib    # Exported pipeline dictionary (model, scaler, metrics)
├── notebooks/             # 📓 Exploratory notebooks
│   └── notebook.ipynb     # Data exploration & initial ML prototyping
├── src/                   # 🌐 Application source code
│   ├── __init__.py
│   ├── app.py             # Flask Web Application & REST API endpoints
│   └── model_pipeline.py  # Data preprocessing, training, & inference logic
├── static/                # 🖼️ Static assets
│   └── app_preview.png    # Preview screenshot
├── templates/             # 🎨 Web UI templates
│   └── index.html         # Interactive dashboard UI (Glassmorphic dark theme)
├── .dockerignore          # 🙈 Excluded files from Docker build context
├── Dockerfile             # 🐳 Production container build recipe (Gunicorn & non-root user)
├── docker-compose.yml     # 🐙 Multi-container service orchestrator setup
└── requirements.txt       # 📦 Python package dependencies
```

---

### 📊 Application Architecture & Flowchart

The diagram below illustrates how requests flow through the containerized architecture from user interaction to machine learning model inference:

```mermaid
flowchart TD
    User([👤 User / Browser]) -->|1. Accesses http://localhost:5000| WebUI[🎨 Flask Web UI / templates/index.html]
    User -->|2. Submits Student Inputs JSON| API Endpoint[🌐 POST /api/predict in src/app.py]

    subgraph Container ["🐳 Docker Container (flask_ml_app)"]
        WSGI[⚙️ Gunicorn WSGI Server]
        WebUI
        API Endpoint

        API Endpoint -->|3. Calls predict_student_score| Pipeline[🤖 src/model_pipeline.py]

        subgraph MLEngine ["🧠 Machine Learning Inference Engine"]
            Pipeline -->|4. Categorical Encoding| Dummies[Categorical One-Hot Encoding]
            Dummies -->|5. Feature Scaling| Scaler[StandardScaler from models/pipeline.joblib]
            Scaler -->|6. Formatted Inputs| Model[LinearRegression Model]
            Model -->|7. Predicts Score| Recommendations[Grade & Insights Generator]
        end

        Recommendations -->|8. Returns JSON Payload| API Endpoint
    end

    API Endpoint -->|9. Renders Animated Dial & Recommendations| User
```

---

### 🔨 Step-by-Step Implementation Guide

#### 1️⃣ Step 1: Create the ML Pipeline (`src/model_pipeline.py`)
Develop a clean pipeline module that trains a `LinearRegression` model using `pandas` and `scikit-learn` on `data/dataset.csv`, then exports the model and scaler artifacts to `models/`:

```python
# src/model_pipeline.py (Key Logic)
import os, joblib, pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_FILE = os.path.join(BASE_DIR, 'data', 'dataset.csv')
PIPELINE_FILE = os.path.join(BASE_DIR, 'models', 'pipeline.joblib')

def train_and_save_pipeline():
    df = pd.read_csv(DATASET_FILE)
    X = df[['study_time_hours', 'attendance_percent', 'sleep_hours', 
            'gender', 'parental_education', 'internet_access', 
            'extracurricular_activities', 'part_time_job']]
    y = df['final_exam_score']

    X_dummies = pd.get_dummies(X, drop_first=True)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_dummies)

    model = LinearRegression()
    model.fit(X_scaled, y)
    joblib.dump({'model': model, 'scaler': scaler}, PIPELINE_FILE)
```

#### 2️⃣ Step 2: Build the Flask Server & UI (`src/app.py` & `templates/index.html`)
Build Flask REST API endpoints (`/api/predict`, `/api/analytics`, `/api/health`) and render the dashboard interface:

```python
# src/app.py
import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

from flask import Flask, render_template, request, jsonify
from model_pipeline import predict_student_score, load_pipeline

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
load_pipeline()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json()
    result = predict_student_score(data)
    return jsonify({'success': True, 'data': result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

#### 3️⃣ Step 3: Specify Dependencies (`requirements.txt`)
Declare necessary Python libraries:

```text
Flask>=3.0.0
gunicorn>=21.2.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
joblib>=1.3.0
```

#### 4️⃣ Step 4: Write the Production Dockerfile (`Dockerfile`)
Apply security and performance best practices (slim Python base image, Gunicorn WSGI server, non-root user, and Docker health check):

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data/ ./data/
COPY models/ ./models/
COPY src/ ./src/
COPY static/ ./static/
COPY templates/ ./templates/

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "src.app:app"]
```

#### 5️⃣ Step 5: Configure Docker Compose (`docker-compose.yml`)
Create a single declarative YAML configuration to manage container deployment:

```yaml
services:
  mlapp:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: flask_ml_app
    ports:
      - "5000:5000"
    environment:
      - PORT=5000
    restart: unless-stopped
```

#### 6️⃣ Step 6: Build & Launch the Application
Run Docker Compose to build the image and spin up the container:

```bash
# Build & start container in background
docker compose up --build -d

# Verify health status
curl http://localhost:5000/api/health
```

---

# 🛠️ THE ULTIMATE DOCKER COMMAND CHEAT SHEET

Use this categorized reference guide during your lectures or when working on containers.

## 1. Image Operations (The Blueprints)
These commands manage your static container recipes (images).

| Command | What it does | Example |
| :--- | :--- | :--- |
| **`docker build -t <name> <path>`** | Builds an image from a `Dockerfile`. | `docker build -t my-todo-app .` |
| **`docker images`** | Lists all local images stored on your machine. | `docker images` |
| **`docker rmi <image_id>`** | Deletes an image from your computer to free space. | `docker rmi my-todo-app` |
| **`docker tag <source> <target>`** | Creates an alias tag pointing to a source image. | `docker tag my-todo:latest user/my-todo:v1` |
| **`docker push <tag_name>`** | Uploads an image to Docker Hub (must login first). | `docker push user/my-todo:v1` |
| **`docker pull <image_name>`** | Downloads an image from Docker Hub. | `docker pull python:3.11-slim` |

---

## 2. Container Management (Running Environments)
These commands control active, running containers.

| Command | What it does | Common Flags | Example |
| :--- | :--- | :--- | :--- |
| **`docker run <image>`** | Creates and starts a new container from an image. | `-d` (background/detached)<br>`-p` (ports)<br>`-v` (volumes)<br>`-e` (env vars)<br>`--name` (rename container) | `docker run -d -p 8080:8000 my-todo` |
| **`docker ps`** | Lists active, running containers. | Add `-a` to show all containers (including stopped ones). | `docker ps -a` |
| **`docker logs <container>`** | Shows terminal outputs/logs from the container. | `-f` (follow logs in real-time) | `docker logs -f running-todo` |
| **`docker stop <container>`** | Gracefully shuts down a running container. | Uses container name or ID. | `docker stop running-todo` |
| **`docker start <container>`** | Starts a container that was previously stopped. | Retains original run configurations. | `docker start running-todo` |
| **`docker restart <container>`**| Reboots a container. | Stops and starts it again. | `docker restart running-todo` |
| **`docker rm <container>`** | Deletes a stopped container. | Add `-f` (force) to delete a running container. | `docker rm -f running-todo` |
| **`docker exec -it <name> <cmd>`**| Runs a command *inside* an already running container. | `-it` (interactive tty - lets you type) | `docker exec -it running-todo bash` |

---

## 3. Storage Persistence (Volumes)
These commands manage persistent folders stored outside container layers.

| Command | What it does | Example |
| :--- | :--- | :--- |
| **`docker volume ls`** | Lists all local volumes created by Docker. | `docker volume ls` |
| **`docker volume create <name>`** | Manually creates a new volume. | `docker volume create todo_storage` |
| **`docker volume inspect <name>`** | Shows detailed information (like physical host path). | `docker volume inspect todo_storage` |
| **`docker volume rm <name>`** | Deletes a volume. *(Fails if volume is attached to a container)*. | `docker volume rm todo_storage` |
| **`docker volume prune`** | Deletes all unused volumes in one go. | `docker volume prune` |

---

## 4. Multi-Container Orchestration (Docker Compose)
These commands manage multi-container setups defined in a `docker-compose.yml` file.

| Command | What it does | Example |
| :--- | :--- | :--- |
| **`docker compose up`** | Starts all services declared in `docker-compose.yml`. | Add `--build` to rebuild images first.<br>Add `-d` to run in background. |
| **`docker compose down`** | Stops and removes all containers, networks, and configurations created by `up`. | `docker compose down` |
| **`docker compose ps`** | Lists the status of containers belonging to this compose file. | `docker compose ps` |
| **`docker compose logs`** | Merges and prints logs from all services in real-time. | `docker compose logs -f` |
| **`docker compose restart`** | Restarts all compose services. | `docker compose restart` |

---

## 5. System Maintenance & Cleanup
Useful commands to clear cached folders and save disk space.

*   **`docker system prune`**: Removes all stopped containers, unused networks, and dangling images. Excellent for cleanups!
    ```bash
    docker system prune -f
    ```
*   **`docker system df`**: Displays disk space usage by containers, images, and volumes.
    ```bash
    docker system df
    ```
