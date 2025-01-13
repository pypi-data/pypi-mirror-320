import base64
import io
import logging
from dataclasses import dataclass
from enum import Enum

import mkdocs.utils
import qrcode
import qrcode.image.svg
from PIL import ImageFont, Image, ImageDraw
from qrcode.main import QRCode

log = logging.getLogger(f"mkdocs.plugins.{__name__}")
log.addFilter(mkdocs.utils.warning_filter)


@dataclass
class Size:
    width: int = 250
    height: int = 250


class SizeStandard(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class CodeType(Enum):
    QR = "QrCode"
    # DATAMATRIX = "DATAMATRIX"
    # PDF = "PDF"


class ImageType(Enum):
    PNG = "PNG"
    SVG = "SVG"


@dataclass
class QRData:
    data: str
    reference: str = None
    title: str = "QrCode"


class QRImageGenerator:
    font_size = 30
    font_box_height = 30

    def __init__(self, code_type: CodeType = CodeType.QR, output_type: ImageType = ImageType.SVG, size: Size | SizeStandard = SizeStandard.SMALL):
        self.code_type = code_type
        self.output_type = output_type

        if type(size) == SizeStandard:
            match size:
                case SizeStandard.LARGE:
                    size = Size(400, 400)
                case SizeStandard.MEDIUM:
                    size = Size(250, 250)
                case SizeStandard.SMALL:
                    size = Size(100, 100)
                case _:
                    size = Size()

        self.size = size or Size()

        self.factory = None
        if output_type == ImageType.SVG:
            self.factory = qrcode.image.svg.SvgImage
            self.factory.background = "white"

    def get_html_tag(self, qr_data: QRData) -> str:
        base_64_qr_code = self._get_qr_code_base_64_data(qr_data=qr_data)

        css_style = f'style="width:{self.size.height}px;height:{self.size.width}px;"'

        match self.output_type:
            case ImageType.SVG:
                image_tag = f'<img src="data:image/svg+xml;base64,{base_64_qr_code}" alt="{qr_data.title}" height="{self.size.height}" width="{self.size.width}" {css_style}>'
            case ImageType.PNG:
                image_tag = f'<img src="data:image/png;base64,{base_64_qr_code}"  alt="{qr_data.title}" {css_style}>'
            case _:
                image_tag = f'Output type not implemented {self.output_type.value}'

        return image_tag

    def _get_qr_code_base_64_data(self, qr_data: QRData) -> str:
        img = self._generate_qr_code_image(qr_data=qr_data)

        if self.output_type != ImageType.SVG:
            img = img.resize((self.size.width, self.size.width))

            if qr_data.reference is not None:
                img = self._add_reference_text(img, qr_data=qr_data)

        base64_str = self._encode_image_to_base_64_png(img=img)
        return base64_str

    def _encode_image_to_base_64_png(self, img):
        img_io = io.BytesIO()
        # img.save(img_io, 'PNG')
        img.save(img_io, self.output_type.value)

        img_io.seek(0)
        img_bytes = img_io.read()
        base64_str = base64.b64encode(img_bytes).decode('utf-8')
        return base64_str

    def _generate_qr_code_image(self, qr_data: QRData):
        qr = QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
            image_factory=self.factory
        )
        qr.add_data(qr_data.data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        return img

    def _add_reference_text(self, img, qr_data: QRData):
        """
Add reference text to QR code.
Also modifies the size of the QR code.
        :param img:
        :param qr_data:
        :return:
        """
        font = ImageFont.truetype("arial.ttf", self.font_size)

        # Create a new image with enough space for the reference text
        new_img = Image.new("RGB", (img.width, img.height + self.font_box_height), "white")
        new_img.paste(img, (0, 0))
        # Draw the reference text
        draw = ImageDraw.Draw(new_img)
        draw.text(
            (20, img.height - 5),
            qr_data.reference,
            fill="black",
            font=font,
        )

        return new_img
