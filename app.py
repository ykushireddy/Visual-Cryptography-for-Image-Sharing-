import os
import cv2
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from core.vc_algo import generate_shares, reconstruct_image

# ---------------------------------------------------------
# Flask App Configuration
# ---------------------------------------------------------
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # Limit uploads to 16 MB

# Ensure the upload directory exists before the app starts
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """
    Helper Function: Checks if the uploaded file has an allowed extension.
    This prevents users from uploading malicious scripts.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------------------------------------------
# Application Routes
# ---------------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main Route: Handles the core functionality of the web UI.
    - GET: Displays the initial upload form.
    - POST: Processes the uploaded secret image, generates shares, and displays them.
    """
    if request.method == 'POST':
        # 1. Validation: Ensure a file was actually submitted in the form
        if 'secret_image' not in request.files:
            return redirect(request.url)
            
        file = request.files['secret_image']
        
        # 2. Validation: Ensure the user selected a valid file
        if file.filename == '' or not allowed_file(file.filename):
            return redirect(request.url)
            
        # 3. Securely Save Uploaded File
        # secure_filename() prevents directory traversal attacks (e.g. "../../../etc/passwd")
        filename = secure_filename(file.filename)
        secret_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(secret_path)
        
        # 4. Process the image using our Visual Cryptography core algorithm
        try:
            # generate_shares() takes the image path and returns the binary thresholded image, 
            # and the two generated random-noise shares.
            thresh, share1, share2 = generate_shares(secret_path)
        except Exception as e:
            return render_template('index.html', error_msg=str(e))
            
        # 5. Define filenames for the generated shares
        share1_filename = 'share1_' + filename
        share2_filename = 'share2_' + filename
        share1_path = os.path.join(app.config['UPLOAD_FOLDER'], share1_filename)
        share2_path = os.path.join(app.config['UPLOAD_FOLDER'], share2_filename)
        
        # 6. Save the newly generated shares to the static/uploads folder using OpenCV
        cv2.imwrite(share1_path, share1)
        cv2.imwrite(share2_path, share2)
        
        # 7. Render the template and pass the image filenames so they can be displayed on the page
        return render_template('index.html', 
                               secret_img=filename, 
                               share1_img=share1_filename, 
                               share2_img=share2_filename)
                               
    # If the method is GET, just show the blank form
    return render_template('index.html')

@app.route('/reconstruct', methods=['POST'])
def reconstruct():
    """
    Reconstruction Route: Handles the simulation of overlaying two shares.
    """
    # 1. Retrieve the filenames of the generated shares from a hidden form input
    share1_filename = request.form.get('share1')
    share2_filename = request.form.get('share2')
    
    if not share1_filename or not share2_filename:
        return redirect(url_for('index'))
        
    share1_path = os.path.join(app.config['UPLOAD_FOLDER'], share1_filename)
    share2_path = os.path.join(app.config['UPLOAD_FOLDER'], share2_filename)
    
    # 2. Call the reconstruction algorithm (which performs a bitwise AND to simulate physical overlay)
    reconstructed = reconstruct_image(share1_path, share2_path)
    
    # 3. Save the reconstructed image
    # Extract the original filename base to keep naming consistent
    original_base = share1_filename.replace('share1_', '')
    recon_filename = 'reconstructed_' + original_base
    recon_path = os.path.join(app.config['UPLOAD_FOLDER'], recon_filename)
    cv2.imwrite(recon_path, reconstructed)
    
    # 4. Render the page showing all images, including the new reconstructed one
    return render_template('index.html', 
                           reconstructed_img=recon_filename,
                           share1_img=share1_filename,
                           share2_img=share2_filename,
                           secret_img=original_base)

if __name__ == '__main__':
    app.run(debug=True)
