FROM python:3.11-slim

# chaingin work dir
WORKDIR /app

COPY uv.lock .

# installing packages from uv
RUN pip install --no-cache-dir uv \
    uv sync

# coping all the file to the container
COPY . .

EXPOSE 8501

# running using uv
CMD ["uv", "run", "streamlit", "run", "main.py", "--server.address=0.0.0.0"]
