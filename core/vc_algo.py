import cv2
import numpy as np
import random
import os

def is_image_complex(img):
    """
    Heuristic check to reject complex photographs/charts.
    Calculates edge density using Canny edge detection.
    """
    edges = cv2.Canny(img, 100, 200)
    edge_density = np.sum(edges > 0) / edges.size
    return edge_density > 0.12  # Reject if more than 12% of the image contains dense edges

def generate_shares(image_path):
    """
    Reads an image, converts it to binary, and generates two visual cryptography shares.
    Uses 2x2 pixel expansion.
    """
    # 1. Read image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not read the image from {image_path}")
        
    # --- BUG FIX: Prevent "Smooth Gray" Issue ---
    # High-resolution images cause 1-pixel alternating noise to visually blend into a smooth gray.
    # We must resize the image down first so the noise blocks remain large relative to the image size.
    max_dim = 200
    h, w = img.shape
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_NEAREST)
        
    # 2. Preprocess: Reject overly complex images
    if is_image_complex(img):
        raise ValueError("Image is too complex or detailed. To guarantee reconstruction clarity, please upload simple text, a basic logo, or a QR code.")
        
    # 3. Convert to strict binary (black and white) using Otsu's thresholding
    # Pixels will be exactly 0 (Black) or 255 (White)
    _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    height, width = thresh.shape
    
    # 3. Initialize shares (2x height and 2x width due to 2x2 pixel expansion)
    share1 = np.zeros((height * 2, width * 2), dtype=np.uint8)
    share2 = np.zeros((height * 2, width * 2), dtype=np.uint8)
    
    # 4. Define the 6 possible 2x2 patterns with exactly 2 white and 2 black pixels
    # (255 = White/Transparent, 0 = Black/Opaque)
    patterns = [
        np.array([[255, 255], [0, 0]], dtype=np.uint8),     # Top white, bottom black
        np.array([[0, 0], [255, 255]], dtype=np.uint8),     # Top black, bottom white
        np.array([[255, 0], [255, 0]], dtype=np.uint8),     # Left white, right black
        np.array([[0, 255], [0, 255]], dtype=np.uint8),     # Left black, right white
        np.array([[255, 0], [0, 255]], dtype=np.uint8),     # Diagonal 1
        np.array([[0, 255], [255, 0]], dtype=np.uint8)      # Diagonal 2
    ]
    
    # 5. Generate shares pixel by pixel
    for i in range(height):
        for j in range(width):
            pixel = thresh[i, j]
            
            # Pick a random pattern for Share 1
            pat = random.choice(patterns)
            share1[i*2:i*2+2, j*2:j*2+2] = pat
            
            # Determine Share 2 based on the original pixel color
            if pixel == 255: 
                # White pixel: Share 2 gets the SAME pattern.
                # When overlaid, the pattern remains half-white, half-black (appears grey/white).
                share2[i*2:i*2+2, j*2:j*2+2] = pat
            else: 
                # Black pixel: Share 2 gets the INVERSE pattern.
                # When overlaid, a white pixel in S1 aligns with a black in S2, resulting in all black.
                inv_pat = 255 - pat
                share2[i*2:i*2+2, j*2:j*2+2] = inv_pat
                
    # --- BUG FIX: Make Noise Chunky ---
    # Scale up the generated shares using nearest-neighbor interpolation.
    # This physically saves the file with 3x3 pixel blocks instead of 1x1,
    # preventing browsers and image viewers from anti-aliasing the noise into a flat gray block.
    scale_up = 3
    share1 = cv2.resize(share1, (width * 2 * scale_up, height * 2 * scale_up), interpolation=cv2.INTER_NEAREST)
    share2 = cv2.resize(share2, (width * 2 * scale_up, height * 2 * scale_up), interpolation=cv2.INTER_NEAREST)
    
    return thresh, share1, share2

def reconstruct_image(share1_path, share2_path):
    """
    Reconstructs the original image by overlaying the two shares.
    Physical overlay is simulated using a bitwise AND operation.
    """
    s1 = cv2.imread(share1_path, cv2.IMREAD_GRAYSCALE)
    s2 = cv2.imread(share2_path, cv2.IMREAD_GRAYSCALE)
    
    if s1 is None or s2 is None:
        raise ValueError("Could not read the shares for reconstruction.")
        
    # Bitwise AND simulates stacking two transparencies:
    # Light passes (255) ONLY if both transparencies let light pass (255 AND 255)
    # If either is opaque (0), light is blocked (0)
    reconstructed = cv2.bitwise_and(s1, s2)
    return reconstructed

# For local testing if the script is run directly
if __name__ == "__main__":
    # Create a simple test image using numpy
    print("Running a quick local test...")
    test_img_path = "test_input.png"
    
    # Create a 100x100 white image with a black square in the middle
    test_img = np.ones((100, 100), dtype=np.uint8) * 255
    test_img[30:70, 30:70] = 0
    cv2.imwrite(test_img_path, test_img)
    
    # Generate shares
    orig, s1, s2 = generate_shares(test_img_path)
    
    # Save shares
    cv2.imwrite("share1.png", s1)
    cv2.imwrite("share2.png", s2)
    
    # Reconstruct
    recon = reconstruct_image("share1.png", "share2.png")
    cv2.imwrite("reconstructed.png", recon)
    
    print("Test complete. Check test_input.png, share1.png, share2.png, and reconstructed.png.")
    
    # Cleanup after test
    # os.remove("test_input.png")
    # os.remove("share1.png")
    # os.remove("share2.png")
    # os.remove("reconstructed.png")
