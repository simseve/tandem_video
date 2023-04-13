import qrcode
import uuid
import json
from PIL import Image

# Generate a URL and a secret UUID
url = "https://example.com"
secret_uuid = str(uuid.uuid4())

# Create a JSON object containing the URL and the secret UUID
data = {
    "url": url,
    "secret": secret_uuid
}
json_data = json.dumps(data)

# Generate the QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(json_data)
qr.make(fit=True)

# Save the QR code as an image
img = qr.make_image(fill_color="black", back_color="white")
img.save("qr_code.png")

# Display the QR code image (optional)
img.show()