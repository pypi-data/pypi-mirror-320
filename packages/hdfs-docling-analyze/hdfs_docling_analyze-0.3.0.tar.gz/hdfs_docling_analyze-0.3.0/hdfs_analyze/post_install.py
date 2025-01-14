import subprocess
import os

def install_tesserocr():
    # Đường dẫn đến file .whl
    whl_path = os.path.join(os.path.dirname(__file__), "third_party", "tesserocr-2.7.1-cp311-cp311-win-amd64.whl")
    try:
        # Cài đặt file .whl
        subprocess.check_call(["pip", "install", whl_path])
        print("Successfully installed tesserocr.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install tesserocr: {e}")

if __name__ == "__main__":
    install_tesserocr()
