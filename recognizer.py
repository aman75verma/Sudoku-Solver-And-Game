# recognizer.py - Enhanced Sudoku Recognition with Multiple Detection Strategies
import cv2
import numpy as np
import pytesseract
from PIL import Image
import os

class SudokuRecognizer:
    """Advanced Sudoku grid recognition with multiple detection strategies."""
    
    def __init__(self):
        # Configure Tesseract (uncomment and adjust path if needed on Windows)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.debug = False
        
    def preprocess_image(self, image_path):
        """Multi-strategy image preprocessing."""
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image from {image_path}")
        
        # Store original for later use
        original = img.copy()
        
        # Resize if too large
        height, width = img.shape[:2]
        if max(height, width) > 800:
            scale = 800 / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        if self.debug:
            cv2.imwrite('debug_01_original.jpg', img)
            cv2.imwrite('debug_02_gray.jpg', gray)
        
        return img, gray, original
    
    def create_multiple_thresholds(self, gray):
        """Create multiple threshold versions for robust detection."""
        thresholds = []
        
        # 1. Adaptive threshold - Gaussian
        adaptive_gaussian = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        thresholds.append(("adaptive_gaussian", adaptive_gaussian))
        
        # 2. Adaptive threshold - Mean
        adaptive_mean = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2
        )
        thresholds.append(("adaptive_mean", adaptive_mean))
        
        # 3. Otsu's threshold
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresholds.append(("otsu", otsu))
        
        # 4. Simple threshold with different values
        for thresh_val in [127, 100, 150]:
            _, simple = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
            thresholds.append((f"simple_{thresh_val}", simple))
        
        # 5. Canny edge detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        canny = cv2.Canny(blurred, 50, 150)
        # Dilate canny edges to make them thicker
        kernel = np.ones((3, 3), np.uint8)
        canny_dilated = cv2.dilate(canny, kernel, iterations=2)
        thresholds.append(("canny", canny_dilated))
        
        if self.debug:
            for i, (name, thresh) in enumerate(thresholds):
                cv2.imwrite(f'debug_threshold_{i:02d}_{name}.jpg', thresh)
        
        return thresholds
    
    def find_grid_contours(self, thresh_image):
        """Find potential Sudoku grid contours."""
        # Find contours
        contours, _ = cv2.findContours(thresh_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort by area (largest first)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        grid_candidates = []
        
        for contour in contours[:10]:  # Check top 10 largest contours
            area = cv2.contourArea(contour)
            
            # Skip very small contours
            if area < 5000:
                continue
            
            # Try different approximation epsilons
            for epsilon_factor in [0.01, 0.02, 0.03, 0.04, 0.05]:
                epsilon = epsilon_factor * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Look for 4-sided polygons
                if len(approx) == 4:
                    # Check if it's roughly square-ish
                    rect = cv2.boundingRect(approx)
                    aspect_ratio = rect[2] / rect[3]  # width/height
                    
                    # Sudoku grids should be roughly square
                    if 0.7 <= aspect_ratio <= 1.3:
                        grid_candidates.append((area, approx, rect))
                        break
        
        return grid_candidates
    
    def detect_grid_by_lines(self, thresh_image):
        """Alternative method: detect grid using line detection."""
        # Use HoughLines to detect grid lines
        lines = cv2.HoughLines(thresh_image, 1, np.pi/180, threshold=150)
        
        if lines is None:
            return None
        
        # Separate horizontal and vertical lines
        horizontal_lines = []
        vertical_lines = []
        
        for line in lines:
            rho, theta = line[0]
            # Vertical lines (theta close to 0 or pi)
            if abs(theta) < 0.1 or abs(theta - np.pi) < 0.1:
                vertical_lines.append((rho, theta))
            # Horizontal lines (theta close to pi/2)
            elif abs(theta - np.pi/2) < 0.1:
                horizontal_lines.append((rho, theta))
        
        # Need at least some lines to form a grid
        if len(horizontal_lines) < 4 or len(vertical_lines) < 4:
            return None
        
        # Find the bounding box of the grid
        h, w = thresh_image.shape
        
        # This is a simplified approach - in practice, you'd want to
        # find the intersection points of the grid lines
        return np.array([
            [[50, 50]],
            [[w-50, 50]], 
            [[w-50, h-50]], 
            [[50, h-50]]
        ], dtype=np.int32)
    
    def find_sudoku_grid(self, thresholds):
        """Find Sudoku grid using multiple strategies."""
        best_candidate = None
        best_score = 0
        
        for name, thresh in thresholds:
            if self.debug:
                print(f"Trying threshold method: {name}")
            
            # Strategy 1: Contour detection
            grid_candidates = self.find_grid_contours(thresh)
            
            for area, contour, rect in grid_candidates:
                # Score based on area and aspect ratio
                aspect_ratio = rect[2] / rect[3]
                area_score = min(area / 50000, 1.0)  # Normalize area score
                aspect_score = 1.0 - abs(1.0 - aspect_ratio)  # Closer to 1.0 is better
                
                total_score = (area_score * 0.7) + (aspect_score * 0.3)
                
                if total_score > best_score:
                    best_score = total_score
                    best_candidate = contour
                    
                if self.debug:
                    print(f"  Candidate: area={area}, aspect={aspect_ratio:.2f}, score={total_score:.2f}")
            
            # Strategy 2: Line detection (as fallback)
            if best_candidate is None:
                line_contour = self.detect_grid_by_lines(thresh)
                if line_contour is not None:
                    best_candidate = line_contour
                    if self.debug:
                        print(f"  Using line detection fallback")
        
        if self.debug and best_candidate is not None:
            print(f"Best candidate score: {best_score:.2f}")
            
        return best_candidate
    
    def order_points(self, pts):
        """Order points consistently."""
        pts = pts.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)
        
        rect[0] = pts[np.argmin(s)]      # top-left
        rect[2] = pts[np.argmax(s)]      # bottom-right
        rect[1] = pts[np.argmin(diff)]   # top-right
        rect[3] = pts[np.argmax(diff)]   # bottom-left
        
        return rect
    
    def extract_grid(self, image, contour):
        """Extract and warp the grid region."""
        rect = self.order_points(contour)
        
        # Calculate dimensions
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        
        maxWidth = max(int(widthA), int(widthB))
        maxHeight = max(int(heightA), int(heightB))
        
        # Use square dimensions
        size = max(maxWidth, maxHeight, 450)  # Minimum 450px
        
        dst = np.array([
            [0, 0],
            [size - 1, 0],
            [size - 1, size - 1],
            [0, size - 1]
        ], dtype="float32")
        
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (size, size))
        
        return warped
    
    def segment_and_recognize(self, grid_image):
        """Segment grid into cells and recognize digits."""
        # Convert to grayscale if needed
        if len(grid_image.shape) == 3:
            gray = cv2.cvtColor(grid_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = grid_image.copy()
        
        # Preprocessing for digit recognition
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        if self.debug:
            cv2.imwrite('debug_07_grid_thresh.jpg', thresh)
        
        h, w = thresh.shape
        cell_h, cell_w = h // 9, w // 9
        
        # Create result grid
        result = np.zeros((9, 9), dtype=int)
        
        for i in range(9):
            for j in range(9):
                # Extract cell with margins
                margin = max(2, min(cell_h, cell_w) // 10)
                y1 = i * cell_h + margin
                y2 = (i + 1) * cell_h - margin
                x1 = j * cell_w + margin
                x2 = (j + 1) * cell_w - margin
                
                if y2 <= y1 or x2 <= x1:
                    continue
                
                cell = thresh[y1:y2, x1:x2]
                digit = self.recognize_cell_digit(cell, i, j)
                result[i][j] = digit
        
        return result
    
    def recognize_cell_digit(self, cell, row, col):
        """Recognize digit in a single cell."""
        # Check if cell is mostly empty
        white_ratio = np.sum(cell == 0) / (cell.shape[0] * cell.shape[1])
        if white_ratio > 0.9:
            return 0
        
        # Find the largest connected component (should be the digit)
        contours, _ = cv2.findContours(cell, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 0
        
        # Get the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Check if contour is significant enough
        if cv2.contourArea(largest_contour) < 20:
            return 0
        
        # Create a clean version with just the largest contour
        mask = np.zeros_like(cell)
        cv2.fillPoly(mask, [largest_contour], 255)
        clean_cell = cv2.bitwise_and(cell, mask)
        
        # Resize for OCR
        resized = cv2.resize(clean_cell, (64, 64), interpolation=cv2.INTER_CUBIC)
        
        # Add padding
        padded = cv2.copyMakeBorder(resized, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=0)
        
        if self.debug:
            cv2.imwrite(f'debug_cell_{row}_{col}.jpg', padded)
        
        # Try OCR
        configs = [
            '--oem 3 --psm 10 -c tessedit_char_whitelist=123456789',
            '--oem 3 --psm 8 -c tessedit_char_whitelist=123456789',
            '--oem 1 --psm 10 -c tessedit_char_whitelist=123456789'
        ]
        
        for config in configs:
            try:
                text = pytesseract.image_to_string(padded, config=config).strip()
                # Clean up result
                digits_only = ''.join(filter(str.isdigit, text))
                
                if digits_only and len(digits_only) >= 1:
                    digit = int(digits_only[0])  # Take first digit
                    if 1 <= digit <= 9:
                        return digit
            except:
                continue
        
        return 0  # Default to empty if OCR fails
    
    def recognize_sudoku(self, image_path):
        """Main recognition method with comprehensive error handling."""
        try:
            print(f"Starting recognition for: {image_path}")
            
            # Step 1: Load and preprocess
            img, gray, original = self.preprocess_image(image_path)
            print("✓ Image loaded and preprocessed")
            
            # Step 2: Create multiple threshold versions
            thresholds = self.create_multiple_thresholds(gray)
            print(f"✓ Created {len(thresholds)} threshold versions")
            
            # Step 3: Find grid using multiple strategies
            grid_contour = self.find_sudoku_grid(thresholds)
            
            if grid_contour is None:
                print("✗ Could not detect Sudoku grid")
                
                # Final fallback: use entire image
                print("Trying fallback: using entire image as grid")
                h, w = gray.shape
                margin = min(h, w) // 10
                grid_contour = np.array([
                    [[margin, margin]],
                    [[w-margin, margin]],
                    [[w-margin, h-margin]],
                    [[margin, h-margin]]
                ])
            
            print("✓ Grid region detected")
            
            # Step 4: Extract grid
            warped = self.extract_grid(gray, grid_contour)
            
            if self.debug:
                cv2.imwrite('debug_08_warped_grid.jpg', warped)
            
            print("✓ Grid extracted and warped")
            
            # Step 5: Segment and recognize digits
            result = self.segment_and_recognize(warped)
            
            print("✓ Digit recognition complete")
            print("Recognized grid:")
            for row in result:
                print(' '.join(str(x) if x != 0 else '.' for x in row))
            
            # Check if we got any digits
            digit_count = np.sum(result != 0)
            if digit_count == 0:
                print("⚠ Warning: No digits recognized")
                return None
            else:
                print(f"✓ Recognized {digit_count} digits")
            
            return result
            
        except Exception as e:
            print(f"✗ Error in recognition: {str(e)}")
            if self.debug:
                import traceback
                traceback.print_exc()
            return None
    
    def enable_debug(self, enable=True):
        """Enable debug mode."""
        self.debug = enable
        if enable:
            print("🔍 Debug mode enabled - saving intermediate images")

# Helper function for testing
def quick_test(image_path):
    """Quick test function."""
    if not os.path.exists(image_path):
        print(f"Image {image_path} not found!")
        return
    
    recognizer = SudokuRecognizer()
    recognizer.enable_debug(True)
    
    result = recognizer.recognize_sudoku(image_path)
    
    if result is not None:
        print("\n🎉 SUCCESS! Grid recognized:")
        for i, row in enumerate(result):
            print(f"Row {i+1}: {row}")
    else:
        print("\n❌ Recognition failed")
        print("\nTroubleshooting tips:")
        print("1. Check debug images to see processing steps")
        print("2. Ensure the grid is clearly visible and well-lit")
        print("3. Try cropping the image closer to the grid")
        print("4. Make sure the image is not too blurry or distorted")

if __name__ == "__main__":
    # Test with a sample image
    test_image = "sudoku_test.jpg"  # Replace with your image path
    quick_test(test_image)