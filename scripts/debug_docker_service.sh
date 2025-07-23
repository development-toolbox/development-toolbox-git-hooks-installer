#!/bin/bash
set -e

echo "Checking dockerd binary..."
if [ -x /usr/bin/dockerd ]; then
    echo "dockerd exists and is executable."
else
    echo "dockerd is missing or not executable!"
    exit 1
fi

echo
echo "Checking for missing libraries with ldd:"
ldd /usr/bin/dockerd | grep "not found" && echo "Some libraries are missing!" || echo "All libraries found."

echo
echo "Attempting to run dockerd manually (may fail, but will show errors):"
sudo /usr/bin/dockerd --version || true

echo
echo "Checking Docker service status:"
sudo systemctl status docker.service || true

echo
echo "Showing recent Docker service logs:"
sudo journalctl -u docker.service --no-pager -n 50 || true

echo
echo "Checking kernel version:"
uname -a

echo
echo "Checking OS version:"
cat /etc/os-release

echo
echo "If you see missing libraries above, try installing them with 'sudo dnf install <library>'."
echo "If dockerd fails to run, check for compatibility issues with AlmaLinux 10."
