FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install C++ compilers and CMake required to build llama.cpp
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Set compilation flags for CPU vector instructions (AVX2 makes it much faster)
ENV CMAKE_ARGS="-DGGML_AVX2=on"
ENV FORCE_CMAKE=1

# Install the Python server bindings for llama.cpp
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "llama-cpp-python[server]"

# We don't copy the model into the container (it's too large). 
# We will mount it via Docker Compose.
COPY ./src /app/src

EXPOSE 8000

# Start the OpenAI-compatible API server provided by llama-cpp-python
CMD ["python", "-m", "llama_cpp.server", "--model", "/app/models/model.gguf", "--host", "0.0.0.0", "--port", "8000", "--n_ctx", "4096"]