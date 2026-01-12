import os
import subprocess
import sys
import shutil

def build():
    # 1. Check Tesseract
    tesseract_dir = os.path.join(os.getcwd(), "tesseract")
    if not os.path.exists(tesseract_dir):
        print("Error: 'tesseract' folder not found in project root.")
        print("Please download Tesseract-OCR (Windows binary) and extract/copy it to a 'tesseract' folder here.")
        print("Structure should be: project_root/tesseract/tesseract.exe")
        return

    # 2. PyInstaller Command
    # --onefile: Create a single exe
    # --noconsole: Don't show terminal window
    # --add-data: Bundle the tesseract folder
    # --name: Output name
    
    # Use sys.executable to run PyInstaller as a module
    # This avoids "command not found" issues if Scripts folder isn't in PATH
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=OCRAlertTool",
        f"--add-data=tesseract{os.pathsep}tesseract", 
        "main.py"
    ]
    
    print("Running build command:", " ".join(cmd))
    
    try:
        # shell=True is often needed on Windows to find commands in PATH
        use_shell = (os.name == 'nt')
        subprocess.check_call(cmd, shell=use_shell)
        print("\nBuild Successful! Check the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild Failed: {e}")

if __name__ == "__main__":
    choice = input("Build EXE? Ensure 'tesseract' folder is present. [y/N]: ")
    if choice.lower() == 'y':
        build()
