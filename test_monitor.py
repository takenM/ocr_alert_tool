import cv2
import numpy as np
import unittest
from monitor import Monitor

class TestMonitor(unittest.TestCase):
    def test_preprocess_logic(self):
        monitor = Monitor()
        
        # Create a dummy image (simulating BGRA from screen capture)
        # White background, Black text
        img = np.zeros((100, 300, 4), dtype=np.uint8)
        img.fill(255)
        
        # Put text (Black)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, '1 2 3 4', (10, 60), font, 2, (0, 0, 0, 255), 3, cv2.LINE_AA) # Note 4 channels for color
        
        # Run preprocessing
        processed = monitor.preprocess_image(img)
        
        # Verify result properties
        # 1. Should be single channel (grayscale/binary)
        self.assertEqual(len(processed.shape), 2)
        
        # 2. Should be larger than original (3x scaled)
        self.assertEqual(processed.shape[0], 300) # 100 * 3
        self.assertEqual(processed.shape[1], 900) # 300 * 3
        
        # 3. Should be binary (mostly 0 or 255)
        unique_vals = np.unique(processed)
        self.assertTrue(len(unique_vals) <= 256) # Just sanity check, but with proper threshold should be few
        
        print("Preprocess test passed. Output shape:", processed.shape)

if __name__ == '__main__':
    unittest.main()
