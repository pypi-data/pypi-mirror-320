#!/bin/bash

# Remove domains from /etc/hosts
if grep -q "127.0.0.1 cameras.genx.ai" /etc/hosts; then
    sudo sed -i '/127.0.0.1 cameras.genx.ai/d' /etc/hosts
    echo "Domain entry removed successfully from /etc/hosts"
else
    echo "Domain entry not found in /etc/hosts"
fi
