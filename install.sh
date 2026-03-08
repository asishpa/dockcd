#!/bin/bash

echo "Setting up DockCD..."

sudo mkdir -p /opt/dockcd
sudo useradd -r -s /bin/false dockcd || true
sudo chown -R dockcd:dockcd /opt/dockcd

echo "Setup complete."