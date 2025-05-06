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

- Python 3.8+
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

4. **Load RAW images** using the GUI buttons and adjust channels as needed.


