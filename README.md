# Visual Cryptography for Secret Image Sharing

## Overview

This project implements a 2-out-of-2 Visual Cryptography scheme that securely splits a secret image into two encrypted shares. Individually, the shares reveal no information about the original image. The secret image can only be reconstructed when both shares are combined.

## Features

* 2-out-of-2 Visual Cryptography implementation
* Secure image share generation
* Image reconstruction through share overlay
* No information leakage from individual shares
* Web-based interface using Flask

## Technologies Used

* Python
* Flask
* OpenCV
* NumPy

## Workflow

1. Upload a grayscale or black-and-white image.
2. Convert the image into a binary format.
3. Generate two encrypted image shares.
4. Overlay both shares to reconstruct the original image.

## Project Structure

```text
├── app.py
├── templates/
├── static/
├── uploads/
├── shares/
├── requirements.txt
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
python app.py
```

Open:

```text
http://localhost:5000
```

## Applications

* Secure image sharing
* Confidential document transmission
* Information security systems
* Visual authentication mechanisms

## Future Enhancements

* Color image support
* Multi-share cryptography schemes
* Cloud deployment
* Enhanced user interface
