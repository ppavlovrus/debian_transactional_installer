FROM debian:bookworm-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    sqlite3 \
    ansible \
    systemd \
    systemd-sysv \
    dbus \
    && rm -rf /var/lib/apt/lists/*

# Create installer user
RUN useradd -m -s /bin/bash installer

# Create necessary directories
RUN mkdir -p /var/lib/transactional-installer \
    /var/log/transactional-installer \
    /etc/transactional-installer \
    /etc/transactional-installer/ansible

# Set ownership
RUN chown -R installer:installer /var/lib/transactional-installer \
    /var/log/transactional-installer \
    /etc/transactional-installer

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package in development mode
RUN pip3 install -e .

# Create symlink for easier access
RUN ln -sf /app/cli/main.py /usr/local/bin/transactional-installer

# Switch to installer user
USER installer

# Set default command
ENTRYPOINT ["transactional-installer", "--help"] 