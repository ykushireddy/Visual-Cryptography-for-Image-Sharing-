import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import os
from core.vc_algo import generate_shares, reconstruct_image

class VisualCryptographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visual Cryptography - Secret Image Sharing")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")

        # Variables to store paths and image data
        self.secret_path = None
        self.share1_img = None
        self.share2_img = None
        self.reconstructed_img = None
        
        # Temporary save paths for display purposes
        self.s1_temp = "temp_share1.png"
        self.s2_temp = "temp_share2.png"

        self.setup_ui()

    def setup_ui(self):
        # --- Top Frame for Buttons ---
        btn_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        btn_frame.pack(fill=tk.X)

        self.btn_upload = tk.Button(btn_frame, text="1. Upload Image", command=self.upload_image, width=15, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        self.btn_upload.pack(side=tk.LEFT, padx=10)

        self.btn_generate = tk.Button(btn_frame, text="2. Generate Shares", command=self.generate, state=tk.DISABLED, width=18, bg="#FF9800", fg="white", font=("Arial", 10, "bold"))
        self.btn_generate.pack(side=tk.LEFT, padx=10)

        self.btn_reconstruct = tk.Button(btn_frame, text="3. Reconstruct Secret", command=self.reconstruct, state=tk.DISABLED, width=20, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.btn_reconstruct.pack(side=tk.LEFT, padx=10)

        self.btn_save = tk.Button(btn_frame, text="4. Save Output", command=self.save_output, state=tk.DISABLED, width=15, bg="#9C27B0", fg="white", font=("Arial", 10, "bold"))
        self.btn_save.pack(side=tk.LEFT, padx=10)

        # --- Middle Frame for Image Display ---
        self.display_frame = tk.Frame(self.root, bg="white", bd=2, relief=tk.SUNKEN)
        self.display_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Labels for Images
        self.lbl_secret = tk.Label(self.display_frame, text="Secret Image", bg="white")
        self.lbl_secret.grid(row=0, column=0, padx=10, pady=10)
        
        self.lbl_share1 = tk.Label(self.display_frame, text="Share 1", bg="white")
        self.lbl_share1.grid(row=0, column=1, padx=10, pady=10)
        
        self.lbl_share2 = tk.Label(self.display_frame, text="Share 2", bg="white")
        self.lbl_share2.grid(row=1, column=0, padx=10, pady=10)
        
        self.lbl_recon = tk.Label(self.display_frame, text="Reconstructed", bg="white")
        self.lbl_recon.grid(row=1, column=1, padx=10, pady=10)

        # Ensure grid expands evenly
        self.display_frame.columnconfigure(0, weight=1)
        self.display_frame.columnconfigure(1, weight=1)
        self.display_frame.rowconfigure(0, weight=1)
        self.display_frame.rowconfigure(1, weight=1)

    def display_image_on_label(self, path, label_widget, max_size=(300, 300)):
        """Helper to resize and display an image on a Tkinter label"""
        try:
            img = Image.open(path)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label_widget.config(image=photo, text="")
            label_widget.image = photo # Keep reference to prevent garbage collection
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to display image:\n{e}")

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Secret Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            self.secret_path = file_path
            self.display_image_on_label(self.secret_path, self.lbl_secret)
            self.btn_generate.config(state=tk.NORMAL)
            
            # Reset others
            self.btn_reconstruct.config(state=tk.DISABLED)
            self.btn_save.config(state=tk.DISABLED)
            self.lbl_share1.config(image='', text="Share 1")
            self.lbl_share2.config(image='', text="Share 2")
            self.lbl_recon.config(image='', text="Reconstructed")

    def generate(self):
        if not self.secret_path:
            return
            
        try:
            # Call our core algorithm
            _, self.share1_img, self.share2_img = generate_shares(self.secret_path)
            
            # Save temporarily to display with PIL
            cv2.imwrite(self.s1_temp, self.share1_img)
            cv2.imwrite(self.s2_temp, self.share2_img)
            
            # Display
            self.display_image_on_label(self.s1_temp, self.lbl_share1)
            self.display_image_on_label(self.s2_temp, self.lbl_share2)
            
            messagebox.showinfo("Success", "Shares generated successfully! They appear as random noise.")
            self.btn_reconstruct.config(state=tk.NORMAL)
            self.btn_save.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate shares:\n{e}")

    def reconstruct(self):
        try:
            # Reconstruct using the temporarily saved shares
            self.reconstructed_img = reconstruct_image(self.s1_temp, self.s2_temp)
            
            recon_temp = "temp_recon.png"
            cv2.imwrite(recon_temp, self.reconstructed_img)
            
            # Display
            self.display_image_on_label(recon_temp, self.lbl_recon)
            messagebox.showinfo("Success", "Secret reconstructed successfully!")
            
            # Cleanup temp reconstruct
            if os.path.exists(recon_temp):
                os.remove(recon_temp)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reconstruct:\n{e}")

    def save_output(self):
        if self.share1_img is None or self.share2_img is None:
            messagebox.showwarning("Warning", "Generate shares first!")
            return
            
        save_dir = filedialog.askdirectory(title="Select Folder to Save Outputs")
        if save_dir:
            try:
                cv2.imwrite(os.path.join(save_dir, "share1.png"), self.share1_img)
                cv2.imwrite(os.path.join(save_dir, "share2.png"), self.share2_img)
                
                if self.reconstructed_img is not None:
                    cv2.imwrite(os.path.join(save_dir, "reconstructed.png"), self.reconstructed_img)
                    
                messagebox.showinfo("Saved", f"All outputs saved successfully in:\n{save_dir}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save images:\n{e}")

    def on_closing(self):
        # Cleanup temp files
        if os.path.exists(self.s1_temp): os.remove(self.s1_temp)
        if os.path.exists(self.s2_temp): os.remove(self.s2_temp)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualCryptographyApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
