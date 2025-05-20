 #!/bin/bash

 # run.sh - Launches the PyQt application in Docker with X11 forwarding

 # Enable X server access for Docker
 xhost +local:docker &>/dev/null || {
     echo "ERROR: Failed to configure X11 permissions"
     exit 1
 }

 # Run container with GUI support
 docker run -it --rm \
     -e XDG_RUNTIME_DIR=/tmp/runtime-root \
     -e DISPLAY=$DISPLAY \
     -v /tmp/.X11-unix:/tmp/.X11-unix \
     pyqt-app python3 src/main.py

 # Reset X server access (optional security measure)
 xhost -local:docker &>/dev/null