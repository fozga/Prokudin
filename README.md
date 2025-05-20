# RGB Channel Processor

**RGB Channel Processor** is a desktop application for advanced processing of RAW images from Sony cameras. The app allows you to load RAW files, split them into RGB channels, align and adjust each channel individually (brightness, contrast, intensity), and preview or export the combined result. The project is built with Python and PyQt5, and is designed to be modular, testable, and user-friendly.

---

## Features

- **Load Sony RAW (.arw) files** and extract RGB channels
- **Automatic alignment** of channels using feature detection
- **Individual channel adjustments:** brightness, contrast, intensity
- **Live preview** of single channels or the combined RGB image
- **Modern PyQt5 GUI** with intuitive sliders and image viewer
- **Modular codebase** for easy extension and testing

---

## Requirements

- Python 3.8+ (for local runs)
- [PyQt5](https://pypi.org/project/PyQt5/)
- [numpy](https://pypi.org/project/numpy/)
- [opencv-python](https://pypi.org/project/opencv-python/)
- [rawpy](https://pypi.org/project/rawpy/)

Install all dependencies with:

```
pip install -r requirements.txt
```


---

## Usage

### Local (Native) Run

1. **Clone the repository:**
    ```
    git clone https://github.com/fozga/FullSpectrumProcessor.git
    cd FullSpectrumProcessor
    ```

2. **Install dependencies:**
    ```
    pip install -r requirements.txt
    ```

3. **Run the application:**
    ```
    python src/main.py
    ```

---

### Running with Docker

You can run the application in a containerized environment with full GUI support.

1. **Build the Docker image:**
    ```
    docker build -t pyqt-app .
    ```


2. **Run the application in a Docker container:**
    On Linux, you can use the provided script for convenience:
    ```
    ./run.sh
    ```
    Or, manually:
    ```
    xhost +local:docker
    docker run -it --rm
    -e DISPLAY=$DISPLAY
    -e XDG_RUNTIME_DIR=/tmp/runtime-root
    -v /tmp/.X11-unix:/tmp/.X11-unix
    pyqt-app python3 src/main.py
    xhost -local:docker
    ```

    - The provided `run.sh` script automates X11 permissions and container launch.
    - Make sure an X server is running on your host (default on Linux desktops).
    - On macOS or Windows, additional X11 setup (e.g., [XQuartz](https://www.xquartz.org/)) may be required.

3. **Security note:**
   The script temporarily allows Docker containers to access your X server for GUI display, and then revokes this permission after the app closes.

---

## Development Notes

- The Dockerfile and run scripts are provided for easy cross-platform deployment and to avoid local dependency conflicts.
- If you encounter warnings like `QStandardPaths: XDG_RUNTIME_DIR not set`, they are harmless but can be silenced by setting the `XDG_RUNTIME_DIR` environment variable as shown above.

