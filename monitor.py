import cv2
import numpy as np
import pytesseract
import mss
import time
import re
import sys
import os

class Monitor:
    def __init__(self):
        # self.sct = mss.mss() # Removed: Initialized in process() for thread-safety on Windows
        
        
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle (PyInstaller)
            base_path = sys._MEIPASS
            if os.name == 'nt': # Windows
                tesseract_cmd = os.path.join(base_path, 'tesseract', 'tesseract.exe')
            else: # Mac/Linux bundle (if we were to bundle it there)
                tesseract_cmd = os.path.join(base_path, 'tesseract', 'tesseract')
            
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            # Normal development environment
            if os.name == 'nt':
                # Windows default (common installer path)
                default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                if os.path.exists(default_path):
                    pytesseract.pytesseract.tesseract_cmd = default_path
            else:
                # Mac/Linux common paths
                possible_paths = [
                    '/usr/local/bin/tesseract',
                    '/opt/homebrew/bin/tesseract',
                    '/usr/bin/tesseract'
                ]
                for p in possible_paths:
                    if os.path.exists(p):
                        pytesseract.pytesseract.tesseract_cmd = p
                        break

    def process(self, area, callback):
        """
        Captures area, processes image, extracts number.
        Calls callback(value, raw_text).
        Returns True if should stop (alert triggered), False otherwise.
        """
        x1, y1, x2, y2 = area
        width = x2 - x1
        height = y2 - y1
        
        monitor = {"top": y1, "left": x1, "width": width, "height": height}
        
    def preprocess_image(self, img):
        """
        Applies grayscale, resizing, and thresholding to the image.
        Returns the processed image ready for OCR.
        """
    def preprocess_image(self, img):
        """
        Applies grayscale, resizing, and thresholding to the image.
        Returns the processed image ready for OCR.
        """
        # Convert to gray
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        
        # Dynamic resizing based on height
        # Tesseract works best when text height is around 30-70 pixels.
        # We aim for a bit larger to cover padding etc. Let's aim for height=100.
        h, w = gray.shape
        target_height = 100.0
        scale = target_height / float(h)
        
        # Ensure at least 2x scale to improve clarity if original is already close to 100
        if scale < 2.0:
            scale = 2.0
            
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # Threshold (Binarize) using Otsu's binarization for auto threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh

    def process(self, area, callback):
        """
        Captures area, processes image, extracts number.
        Calls callback(value, raw_text).
        Returns True if should stop (alert triggered), False otherwise.
        """
        x1, y1, x2, y2 = area
        width = x2 - x1
        height = y2 - y1
        
        monitor = {"top": y1, "left": x1, "width": width, "height": height}
        
        # Capture
        # Use mss in context manager within the thread to avoid threading issues on Windows
        with mss.mss() as sct:
            sct_img = sct.grab(monitor)
            img = np.array(sct_img)
        
        # DEBUG: Save original capture
        cv2.imwrite("debug_original.png", img)
        
        # Preprocess
        thresh = self.preprocess_image(img)
        
        # DEBUG: Save processed image
        cv2.imwrite("debug_processed.png", thresh)
        
        # OCR
        # psm 6: Assume a single uniform block of text.
        # whitelist: 0-9 . , (restrict to numbers)
        config = '--psm 6 -c tessedit_char_whitelist=0123456789.,'
        try:
            text = pytesseract.image_to_string(thresh, config=config)
        except Exception as e:
            print(f"OCR Error: {e}")
            text = ""

        # Extract Number
        # Find all numbers (integers or floats) in the text
        # We process the raw text because removing spaces might concatenate separate numbers causing errors
        # e.g. "1 2" -> "12" (bad) vs "1", "2" (good)
        # But sometimes "1 2,000" should be "12000".
        # Given the user's log '5\n1\n...', these are likely separate numbers.
        # Let's treat distinct sequences of digits+dots as separate numbers.
        
        matches = re.findall(r'\d+(?:\.\d+)?', text)
        
        values = []
        for m in matches:
            try:
                # Remove common OCR artifacts if needed, but regex handles most.
                # Just parse float
                v = float(m)
                values.append(v)
            except ValueError:
                pass
        
        val = 0.0
        if values:
            val = max(values)
        
        # Debug / Log (can be removed later)
        # print("Raw:", text, "Values:", values, "Max:", val)
        
        # Debug / Log (can be removed later)
        # print("Raw:", text, "Clean:", clean_text, "Val:", val)
        
        # Call UI callback
        should_stop = callback(val, text)
        
        # Sleep a bit to prevent CPU hogging
        time.sleep(1) 
        
        return should_stop
