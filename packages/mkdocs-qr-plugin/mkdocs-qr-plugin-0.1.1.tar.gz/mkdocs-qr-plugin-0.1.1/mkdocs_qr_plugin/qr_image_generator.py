import base64
import io
import logging

import mkdocs.utils
import qrcode
from PIL import ImageFont, Image, ImageDraw
from qrcode.main import QRCode

log = logging.getLogger(f"mkdocs.plugins.{__name__}")
log.addFilter(mkdocs.utils.warning_filter)


class Size:
    def __init__(self, width, height):
        self.width = width
        self.height = height


class QRImageGenerator:
    font_size = 30
    font_box_height = 30

    def __init__(self, data: str, size: Size = None, reference: str = None):
        self.data = data or 'No Data Provided'
        self.size = size or Size(400, 400)
        self.reference = reference or None

    def get_qr_code_base_64_data(self) -> str:
        img = self._generate_qr_code_image()

        img = img.resize((self.size.width, self.size.width))

        if self.reference is not None:
            img = self._add_reference_text(img)

        base64_str = QRImageGenerator._encode_image_base_64_png(img)
        return base64_str

    @staticmethod
    def _encode_image_base_64_png(img):
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        img_bytes = img_io.read()
        base64_str = base64.b64encode(img_bytes).decode('utf-8')
        return base64_str

    def _generate_qr_code_image(self):
        qr = QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        return img

    def _add_reference_text(self, img):
        # Calculate dimensions for reference text
        font = ImageFont.truetype("arial.ttf", self.font_size)

        # Create a new image with enough space for the reference text
        new_img = Image.new("RGB", (img.width, img.height + self.font_box_height), "white")
        new_img.paste(img, (0, 0))
        # Draw the reference text
        draw = ImageDraw.Draw(new_img)
        draw.text(
            (20, img.height - 5),
            self.reference,
            fill="black",
            font=font,
        )
        return new_img
