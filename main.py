import tkinter as tk
from gui import OCRAlertApp

def main():
    root = tk.Tk()
    app = OCRAlertApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
