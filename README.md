# Visual Cryptography for Secret Image Sharing

This is a Computer Networks and Security (CNS) mini-project that demonstrates a **2-out-of-2 Visual Cryptography** scheme.

##  Problem Statement
In secure communication, transmitting sensitive visual data over untrusted channels poses a risk of interception. Traditional encryption algorithms require computational power to decrypt data. The problem addressed in this project is to securely share a secret image such that the encrypted shares reveal absolutely no information when viewed individually, and can be decrypted purely by the human visual system (or simulated digital overlay) without any computational decryption algorithms.

##  Objective
- To implement a 2-out-of-2 visual cryptography algorithm.
- To demonstrate how an image can be split into two random-noise shares.
- To show that only the authorized combination (overlaying both shares) reveals the original secret.

##  Architecture & Workflow
1. **Input**: User uploads a grayscale or black-and-white image.
2. **Binarization**: The image is thresholded into strict black (`0`) and white (`255`) pixels using OpenCV (Otsu's method).
3. **Encryption (Share Generation)**:
   - The algorithm uses a **2x2 pixel expansion**.
   - For every **White** pixel, Share 1 and Share 2 receive the *identical* random pattern (2 white, 2 black sub-pixels).
   - For every **Black** pixel, Share 1 receives a random pattern, and Share 2 receives the *inverted* pattern.
4. **Decryption (Reconstruction)**:
   - The two shares are overlaid using a Bitwise AND operation, which perfectly simulates stacking two physical transparent sheets. 
   - Light passes only where both sheets are transparent (white).

##  Setup & Installation
Follow these steps to run the project locally on your machine:

1. **Ensure Python is installed** (Python 3.7+ recommended).
2. **Open a terminal** and navigate to this project folder.
3. **(Optional but recommended) Create a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # On Windows
   source venv/bin/activate  # On Mac/Linux
   ```
4. **Install the required libraries:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Run the Flask application:**
   ```bash
   python app.py
   ```
6. **Open your browser** and navigate to: `http://localhost:5000`



