# Step-by-Step CI/CD Setup Guide for CCABank

This guide provides a comprehensive, step-by-step walkthrough to build a complete Continuous Integration and Continuous Delivery (CI/CD) pipeline for **CCABank** from scratch. 

We will use **GitHub Actions** as our pipeline orchestrator and **Docker Hub** as our container registry. By the end of this guide, your application will automatically lint, run unit tests, build a Docker container, perform an API health check, and publish the container to Docker Hub on every merge to the `main` branch.

---

## 📋 Prerequisites
Before starting, ensure you have:
1. A **GitHub** account ([github.com](https://github.com/)).
2. A **Docker Hub** account ([hub.docker.com](https://hub.docker.com/)).
3. **Git** installed and configured on your local development machine.
4. **Docker** installed locally (optional, for local testing).

---

## 🛠️ Step 1: Initialize Git and Prepare Your Local Repository

If you haven't already initialized Git in your project folder, follow these steps.

1. Open your terminal and navigate to the project directory:
   ```bash
   cd /home/lalith/Documents/CCA/DevOps/Docker/CCABank
   ```

2. Initialize a local Git repository:
   ```bash
   git init
   ```

3. Create a `.gitignore` file in the root of the project to prevent pushing temporary, local-only files (like virtual environments, databases, or python cache) to GitHub:
   ```bash
   cat <<EOF > .gitignore
   # Python cache
   __pycache__/
   *.py[cod]
   *$py.class
   
   # Databases & Local Settings
   db.sqlite3
   local_settings.py
   
   # Environments
   .venv/
   venv/
   ENV/
   
   # OS files
   .DS_Store
   EOF
   ```

4. Stage and commit your files:
   ```bash
   git add .
   git commit -m "chore: initial commit of CCABank project files"
   ```

---

## 🧪 Step 2: Configure Django for CI/CD Testing

By default, Django applications running unit tests attempt to spin up a test database using the database configuration defined in `settings.py`. Since our main database configuration points to a **MySQL** server (`db_cca_bank`), running tests in the CI pipeline without a live MySQL instance would crash the workflow immediately.

To solve this, we conditionally override the database connection to use a lightweight, in-memory **SQLite** database when running tests.

1. Open `CCABank/MyProject/MyProject/settings.py` and modify the `DATABASES` configuration block to include the `sys.argv` override:
   ```python
   import os
   import sys
   
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': os.environ.get('DB_NAME', 'db_cca_bank'),
           'USER': os.environ.get('DB_USER', 'root'),
           'PASSWORD': os.environ.get('DB_PASSWORD', 'Admin@123'),
           'HOST': os.environ.get('DB_HOST', 'localhost'),
           'PORT': os.environ.get('DB_PORT', '3306'),
       }
   }
   
   # Fallback to SQLite when running unit tests
   if 'test' in sys.argv:
       DATABASES = {
           'default': {
               'ENGINE': 'django.db.backends.sqlite3',
               'NAME': BASE_DIR / 'db.sqlite3',
           }
       }
   ```

2. Open `CCABank/MyProject/bankapp/tests.py` and add unit tests. Since the application views perform raw SQL queries on tables (which won't exist in our empty test SQLite database), we patch `bankapp.db_repository` functions with `unittest.mock`:
   ```python
   from django.test import TestCase
   from unittest.mock import patch
   
   class BankAppTests(TestCase):
       @patch('bankapp.db_repository.getuser')
       def test_homepage_anonymous(self, mock_getuser):
           """Test that the homepage renders successfully for an anonymous user."""
           mock_getuser.return_value = {"login_name": "", "role_name": "ROLE_PUBLIC", "token": "mock-token-123"}
           
           response = self.client.get('/bank/')
           self.assertEqual(response.status_code, 200)
           self.assertContains(response, "You are not logged in. Please log in or register first.")
   
       @patch('bankapp.db_repository.getuser')
       def test_aboutus_page(self, mock_getuser):
           """Test that the about-us page renders successfully."""
           mock_getuser.return_value = {"login_name": "", "role_name": "ROLE_PUBLIC", "token": "mock-token-123"}
           
           response = self.client.get('/bank/about-us')
           self.assertEqual(response.status_code, 200)
           self.assertContains(response, "About Us")
   ```

3. Commit these changes:
   ```bash
   git add MyProject/MyProject/settings.py MyProject/bankapp/tests.py
   git commit -m "test: configure sqlite database fallback and add mock unit tests"
   ```

---

## 🐙 Step 3: Connect Your Repository to GitHub

1. Log in to **GitHub** and click **New** to create a new repository.
   - Name it: `ccabank-devops`.
   - Set it as **Public** or **Private** (depending on your preference).
   - Leave "Add a README", "Add .gitignore", and "Choose a license" **unchecked** (since we already created them locally).
   - Click **Create repository**.

2. Link your local project directory to this new GitHub repository:
   ```bash
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ccabank-devops.git
   ```

3. Rename your default branch to `main` and push your local branch:
   ```bash
   git branch -M main
   git push -u origin main
   ```

---

## 🐳 Step 4: Configure Docker Hub Authentication

GitHub Actions requires authentication to push containers to Docker Hub. We will create a secure Access Token in Docker Hub instead of using your primary password.

1. Log in to [Docker Hub](https://hub.docker.com/).
2. Click on your profile picture in the top-right corner and select **Account Settings**.
3. In the left-hand navigation sidebar, click on **Security**.
4. Click **Personal Access Tokens** -> **Generate new token**.
5. Name the token (e.g., `ccabank-github-actions`) and set permissions to **Read, Write, Delete**.
6. Click **Generate**.
7. **Copy the generated token immediately!** (You will not be able to view it again once you close the window).

---

## 🔑 Step 5: Configure Secrets in GitHub

To keep your Docker credentials secure, you must save them as GitHub Secrets.

1. Navigate to your newly created repository on GitHub.
2. Click on **Settings** in the top tab menu.
3. In the left sidebar, expand **Secrets and variables** and click on **Actions**.
4. Click the green **New repository secret** button.
5. Add the first secret:
   - **Name**: `DOCKERHUB_USERNAME`
   - **Secret**: *Your actual Docker Hub username* (e.g., `lalithtrs`)
6. Click **Add secret**.
7. Click **New repository secret** again to add the second secret:
   - **Name**: `DOCKERHUB_TOKEN`
   - **Secret**: *The Personal Access Token you copied from Docker Hub in Step 4*
8. Click **Add secret**.

---

## ⚙️ Step 6: Create the CI/CD Workflow File

GitHub Actions looks for YAML configuration files in the `.github/workflows/` directory of your repository.

1. Create the workflow directories:
   ```bash
   mkdir -p .github/workflows
   ```

2. Create a file named `.github/workflows/ccabank-cicd.yml` inside the directory:
   ```bash
   touch .github/workflows/ccabank-cicd.yml
   ```

3. Open `.github/workflows/ccabank-cicd.yml` and paste the following configuration:
   ```yaml
   name: CCABank CI/CD Pipeline
   
   on:
     push:
       branches: [ main ]
       paths:
         - 'CCABank/**'
         - '.github/workflows/ccabank-cicd.yml'
     pull_request:
       branches: [ main ]
       paths:
         - 'CCABank/**'
         - '.github/workflows/ccabank-cicd.yml'
   
   jobs:
     # ========================================================
     # JOB 1: LINT & RUN TESTS (CI Stage 1)
     # ========================================================
     lint-and-test:
       name: Lint & Run Unit Tests
       runs-on: ubuntu-latest
       defaults:
         run:
           working-directory: CCABank
   
       steps:
         - name: Checkout Code
           uses: actions/checkout@v4
   
         - name: Set up Python
           uses: actions/setup-python@v5
           with:
             python-version: '3.11'
             cache: 'pip'
   
         - name: Install Dependencies
           run: |
             python -m pip install --upgrade pip
             pip install flake8
             if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
   
         - name: Lint Code with Flake8
           run: |
             # Stop the build on syntax errors or undefined names
             flake8 MyProject --count --select=E9,F63,F7,F82 --show-source --statistics
             # exit-zero treats all errors as warnings
             flake8 MyProject --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
   
         - name: Run Django Tests
           run: |
             python MyProject/manage.py test MyProject/
   
     # ========================================================
     # JOB 2: DOCKER IMAGE BUILD & SMOKE TEST (CI Stage 2)
     # ========================================================
     build-and-validate-docker:
       name: Build & Validate Docker Image
       needs: lint-and-test
       runs-on: ubuntu-latest
   
       steps:
         - name: Checkout Code
           uses: actions/checkout@v4
   
         - name: Set up Docker Buildx
           uses: docker/setup-buildx-action@v3
   
         - name: Build Docker Image Locally
           uses: docker/build-push-action@v5
           with:
             context: CCABank
             file: CCABank/Dockerfile
             tags: ccabank:local
             outputs: type=docker,dest=/tmp/ccabank_image.tar
   
         - name: Load Local Image
           run: |
             docker load --input /tmp/ccabank_image.tar
   
         - name: Start Docker Container (Smoke Test)
           run: |
             # Spin up container on port 8000
             docker run -d --name ccabank_test -p 8000:8000 ccabank:local
             echo "Waiting for Django server to bind..."
             sleep 5
   
         - name: Run Smoke Test API Validation
           run: |
             # Call the homepage endpoint and check for 200 OK or 302 Redirect
             RESPONSE_CODE=$(curl --write-out "%{http_code}" --silent --output /dev/null http://localhost:8000/bank/)
             echo "Django responded with status code: $RESPONSE_CODE"
             if [ "$RESPONSE_CODE" -ne 200 ] && [ "$RESPONSE_CODE" -ne 302 ]; then
               echo "Smoke test validation failed! Received code: $RESPONSE_CODE"
               docker logs ccabank_test
               exit 1
             fi
             echo "Validation successful!"
   
         - name: Tear Down Container
           if: always()
           run: |
             docker stop ccabank_test || true
             docker rm ccabank_test || true
   
     # ========================================================
     # JOB 3: PUBLISH TO DOCKER HUB REGISTRY (CD Stage)
     # ========================================================
     push-to-registry:
       name: Build & Push to Docker Hub
       needs: build-and-validate-docker
       runs-on: ubuntu-latest
       # Execute ONLY when changes are merged/pushed directly to the main branch
       if: github.ref == 'refs/heads/main' && github.event_name == 'push'
   
       steps:
         - name: Checkout Code
           uses: actions/checkout@v4
   
         - name: Log in to Docker Hub
           uses: docker/login-action@v3
           with:
             username: ${{ secrets.DOCKERHUB_USERNAME }}
             password: ${{ secrets.DOCKERHUB_TOKEN }}
   
         - name: Extract metadata (tags, labels) for Docker
           id: meta
           uses: docker/metadata-action@v5
           with:
             images: ${{ secrets.DOCKERHUB_USERNAME }}/ccabank
             tags: |
               type=raw,value=latest
               type=sha,format=short
   
         - name: Build and Push Docker Image
           uses: docker/build-push-action@v5
           with:
             context: CCABank
             file: CCABank/Dockerfile
             push: true
             tags: ${{ steps.meta.outputs.tags }}
             labels: ${{ steps.meta.outputs.labels }}
   ```

---

## 🛠️ Step 7: Push the Configuration & Verify the Pipeline

1. Add, commit, and push your newly created workflow to GitHub:
   ```bash
   git add .github/workflows/ccabank-cicd.yml
   git commit -m "feat: add github actions workflow for ccabank cicd"
   git push origin main
   ```

2. Open your repository on **GitHub** and click on the **Actions** tab at the top.
3. You will see a workflow run starting under the name **"CCABank CI/CD Pipeline"**. Click on it to inspect the logs:
   - Check the **Lint & Run Unit Tests** job to confirm the Django tests execute on sqlite.
   - Check the **Build & Validate Docker Image** job to confirm the container spins up and passes the validation check.
   - Check the **Build & Push to Docker Hub** job to verify that the container is tagged with `latest` and `sha-<git-sha>` and uploaded to your Docker Hub registry.

4. Open your [Docker Hub](https://hub.docker.com/) account. Navigate to your repositories, and confirm the new `ccabank` repository exists with the recently pushed tags!
