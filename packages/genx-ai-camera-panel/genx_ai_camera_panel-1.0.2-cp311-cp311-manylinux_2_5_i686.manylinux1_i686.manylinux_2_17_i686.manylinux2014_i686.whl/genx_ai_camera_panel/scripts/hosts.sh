#!/bin/bash

# Add domains to /etc/hosts if not already present
if ! grep -q "127.0.0.1 cameras.genx.ai" /etc/hosts; then
    echo "127.0.0.1 cameras.genx.ai" | sudo tee -a /etc/hosts
    echo "Domains added successfully to /etc/hosts"
else
    echo "Domain entry already exists in /etc/hosts"
fi
