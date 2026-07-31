# DevOps / Cloud Classes - CCA

Official repository for DevOps and Cloud classes in CCA.

This repository contains lecture materials, hands-on labs, and example notebooks used in the DevOps/Cloud course. The materials are organized as Jupyter Notebooks, supplemental HTML pages, Python helpers, and a small Dockerfile to run the environment.

## Table of Contents

- About
- Repository structure
- Getting started
- Running the notebooks
- Using Docker
- Recommended workflow
- Contributing
- License & Contact

## About

This repository is intended for students and instructors participating in the DevOps / Cloud classes at CCA. It provides a collection of interactive lessons, exercises, and practical examples to teach key DevOps and cloud concepts such as CI/CD basics, containerization, infrastructure-as-code, monitoring, and cloud-native patterns.

## Repository structure

- notebooks/                - Jupyter Notebooks (primary learning materials)
- docs/                     - HTML or generated documentation and slides
- examples/                 - Python examples and helper scripts
- Dockerfile                - Container configuration to run the notebooks locally
- README.md                 - This file

> Language composition: Jupyter Notebook (~87%), HTML (~9%), Python (~4%), Dockerfile (~0.3%)

## Getting started

Prerequisites
- Git
- Python 3.8+ (recommended)
- Jupyter Notebook or JupyterLab
- (Optional) Docker and Docker Compose

Clone the repository:

```bash
git clone https://github.com/lalithtrs/devops-cca.git
cd devops-cca
```

Create a Python virtual environment and install dependencies (if a requirements file is provided):

```bash
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
.\.venv\Scripts\activate   # Windows
# pip install -r requirements.txt  # if present
```

## Running the notebooks

You can run the notebooks locally using Jupyter:

```bash
jupyter notebook    # opens the classic notebook interface
# or
jupyter lab         # opens JupyterLab (if installed)
```

Open the notebooks/ directory in the UI and run the cells in order. Each notebook contains context and instructions for its exercises.

## Using Docker

This repository includes a Dockerfile to simplify environment setup. Build and run the container to host the notebooks in an isolated environment:

```bash
# Build the image
docker build -t devops-cca .

# Run the container and forward notebook port (adjust command as needed)
docker run --rm -p 8888:8888 -v "$(pwd)":/workspace devops-cca
```

After the container starts, open the Jupyter URL printed in the container logs (usually http://127.0.0.1:8888).

## Recommended workflow

- Work in feature branches when making changes to notebooks or examples.
- Keep notebooks clean: avoid committing large transient outputs if not needed.
- Add supplemental Python modules in examples/ and import them from notebooks where appropriate.

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository.
2. Create a branch for your change: `git checkout -b fix/your-change`.
3. Make your changes and add tests or example updates when relevant.
4. Submit a pull request describing the change and why it's needed.

Please follow any course-specific contribution guidelines if provided by the instructor.

## Contact

Maintainer: lalithtrs

For course-related questions or issues, open an issue in this repository and tag the instructor or maintainer.
