# in order to recognize a QR from an image you have to
# pip install pyzbar
# UBUNTU: sudo apt-get install libzbar0
# MAC: brew install zbar

# I had to run this on mac to make zbar working:
#  mkdir ~/lib
# ln -s $(brew --prefix zbar)/lib/libzbar.dylib ~/lib/libzbar.dylib

import json
from pyzbar.pyzbar import decode
from PIL import Image
import os.path

script_dir = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(script_dir, 'test1.png'))

def read_qr_code(image):
    # Read the QR code
    decoded_data = decode(image)
    
    # Check if any QR code is detected
    if not decoded_data:
        return None

    # Decode the JSON data from the QR code
    json_data = decoded_data[0].data.decode('utf-8')
    data = json.loads(json_data)

    return data

# Example usage
data = read_qr_code(im)

if data:
    url = data["url"]
    secret_uuid = data["secret"]

    print("URL:", url)
    print("Secret UUID:", secret_uuid)
else:
    print("No QR code detected")