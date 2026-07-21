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
