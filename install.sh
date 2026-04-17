#!/bin/bash

echo "Setting up DockCD..."

# Create dockcd system user if it doesn't exist

if ! id -u dockcd >/dev/null 2>&1; then
sudo useradd 
--system 
--create-home 
--home-dir /opt/dockcd 
--shell /usr/sbin/nologin 
dockcd
fi

# Ensure directory exists

sudo mkdir -p /opt/dockcd

# Set correct ownership

sudo chown -R dockcd:dockcd /opt/dockcd

# Show UID/GID (needed for Docker build)

echo "DockCD user details:"
id dockcd

echo "Setup complete."
