FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN adduser --quiet --disabled-password qtuser && usermod -a -G audio qtuser

ENV LIBGL_ALWAYS_INDIRECT=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-pyqt5 && \
    rm -rf /var/lib/apt/lists/*

# Install application in system location (hidden from user)
COPY requirements.txt /opt/app/
WORKDIR /opt/app
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/

# Set up user workspace (only input/output will be visible here)
WORKDIR /app
RUN mkdir -p /app/input /app/output && \
    chown qtuser:qtuser /app/input /app/output

# Add application to Python path so it can be imported
ENV PYTHONPATH="/opt/app:$PYTHONPATH"

USER qtuser
CMD ["python3", "-m", "src.main"]